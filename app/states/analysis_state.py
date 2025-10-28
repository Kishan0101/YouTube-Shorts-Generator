import reflex as rx
import logging
from faster_whisper import WhisperModel
from textblob import TextBlob
import numpy as np
import uuid
from app.states.video_state import VideoState, TranscriptionSegment, Clip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

logging.basicConfig(level=logging.INFO)


class AnalysisState(rx.State):
    @rx.event(background=True)
    async def analyze_video(self, project_id: str):
        async with self:
            vs = await self.get_state(VideoState)
            vs.set_processing_video_id(project_id)
            vs._update_project_status(project_id, status="analyzing")
            yield rx.toast.info("Starting analysis...")
        project = next((p for p in vs.video_projects if p["id"] == project_id), None)
        if not project or not project.get("file_path"):
            async with self:
                vs.set_processing_video_id(None)
                vs._update_project_status(
                    project_id,
                    status="error",
                    error_message="Video file not found for analysis.",
                )
                yield rx.toast.error("Analysis failed: Video file missing.")
            return
        try:
            video_path = str(rx.get_upload_dir() / project["file_path"])
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(video_path, word_timestamps=True)
            transcription_segments = [
                TranscriptionSegment(start=s.start, end=s.end, text=s.text)
                for s in segments
            ]
            async with self:
                vs = await self.get_state(VideoState)
                vs._update_project_status(project_id, segments=transcription_segments)
                yield rx.toast.info("Transcription complete. Scoring segments...")
            scored_segments = []
            for seg in transcription_segments:
                blob = TextBlob(seg["text"])
                sentiment = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                sentiment_score = (sentiment + 1) / 2
                subjectivity_score = subjectivity
                word_count = len(seg["text"].split())
                duration = seg["end"] - seg["start"]
                wps = word_count / duration if duration > 0 else 0
                wps_score = min(wps / 5, 1.0)
                loudness_score = 0.5
                engagement_score = (
                    sentiment_score * vs.sentiment_weight
                    + subjectivity_score * vs.subjectivity_weight
                    + wps_score * vs.wps_weight
                )
                scored_segments.append({**seg, "score": engagement_score})
            clips = self._find_best_clips(
                scored_segments, project["duration"], project_id
            )
            async with self:
                vs = await self.get_state(VideoState)
                vs._update_project_status(project_id, status="complete", clips=clips)
                vs.set_processing_video_id(None)
                yield rx.toast.success("Analysis complete! Found best clips.")
        except Exception as e:
            logging.exception(f"Analysis failed for {project_id}: {e}")
            async with self:
                vs = await self.get_state(VideoState)
                vs.set_processing_video_id(None)
                vs._update_project_status(
                    project_id, status="error", error_message=str(e)
                )
                yield rx.toast.error(f"Analysis failed: {e}")

    def _find_best_clips(
        self,
        scored_segments: list[dict],
        video_duration: float,
        project_id: str,
        num_clips=5,
    ) -> list[Clip]:
        if not scored_segments:
            return []
        scores = np.array([s["score"] for s in scored_segments])
        cumsum_scores = np.cumsum(scores)
        best_clips = []
        for _ in range(num_clips):
            best_score = -1
            best_clip_info = None
            for i in range(len(scored_segments)):
                for j in range(i, len(scored_segments)):
                    start_time = scored_segments[i]["start"]
                    end_time = scored_segments[j]["end"]
                    duration = end_time - start_time
                    if 15 <= duration <= 60:
                        total_score = cumsum_scores[j] - (
                            cumsum_scores[i - 1] if i > 0 else 0
                        )
                        avg_score = total_score / (j - i + 1)
                        if avg_score > best_score:
                            text = " ".join(
                                [s["text"] for s in scored_segments[i : j + 1]]
                            )
                            best_score = avg_score
                            best_clip_info = {
                                "start": start_time,
                                "end": end_time,
                                "text": text,
                                "score": avg_score,
                            }
            if best_clip_info:
                best_clips.append(
                    Clip(
                        id=str(uuid.uuid4()),
                        start=best_clip_info["start"],
                        end=best_clip_info["end"],
                        text=best_clip_info["text"],
                        score=best_clip_info["score"],
                        duration_str="",
                        video_id=project_id,
                        status="pending",
                    )
                )
        return sorted(best_clips, key=lambda x: x["score"], reverse=True)

    @rx.event(background=True)
    async def generate_short(self, clip_info: dict):
        video_id = clip_info["video_id"]
        clip_id = clip_info["id"]
        async with self:
            vs = await self.get_state(VideoState)
            vs._update_clip_status(video_id, clip_id, "generating")
            yield rx.toast.info(f"Generating short for clip...")
        try:
            async with self:
                vs = await self.get_state(VideoState)
                project = next(
                    (p for p in vs.video_projects if p["id"] == video_id), None
                )
            if not project or not project.get("file_path"):
                raise ValueError("Original video file not found.")
            video_path = str(rx.get_upload_dir() / project["file_path"])
            video_clip = VideoFileClip(video_path).subclip(
                clip_info["start"], clip_info["end"]
            )
            output_dir = rx.get_upload_dir() / "shorts"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"{video_id}_{clip_id}.mp4"
            output_path = str(output_dir / output_filename)
            video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            async with self:
                vs = await self.get_state(VideoState)
                vs._update_clip_status(video_id, clip_id, "complete")
                yield rx.toast.success("Short generated successfully!")
        except Exception as e:
            logging.exception(f"Error generating short: {e}")
            async with self:
                vs = await self.get_state(VideoState)
                vs._update_clip_status(video_id, clip_id, "error")
                yield rx.toast.error(f"Failed to generate short: {e}")