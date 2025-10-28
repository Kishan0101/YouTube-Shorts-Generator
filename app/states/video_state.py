import reflex as rx
from typing import TypedDict, Literal
import time
import yt_dlp
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
Status = Literal[
    "pending", "downloading", "processing", "analyzing", "complete", "error"
]


class TranscriptionSegment(TypedDict):
    start: float
    end: float
    text: str


class Clip(TypedDict):
    id: str
    start: float
    end: float
    text: str
    score: float
    duration_str: str


class Video(TypedDict):
    id: str
    url: str
    title: str
    thumbnail: str
    duration: int
    duration_str: str
    status: Status
    progress: int
    file_path: str | None
    error_message: str | None
    segments: list[TranscriptionSegment]
    clips: list[Clip]


class VideoState(rx.State):
    video_projects: list[Video] = []
    video_url: str = ""
    is_loading: bool = False
    error: str | None = None
    processing_video_id: str | None = None

    @rx.var
    def has_projects(self) -> bool:
        return len(self.video_projects) > 0

    def _format_duration(self, seconds: int | float) -> str:
        if not isinstance(seconds, (int, float)):
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return (
            f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
            if h > 0
            else f"{int(m):02d}:{int(s):02d}"
        )

    def _format_duration_str(self, seconds: float) -> str:
        m, s = divmod(seconds, 60)
        return f"{int(m):02d}:{int(s):02d}"

    @rx.var
    def formatted_video_projects(self) -> list[Video]:
        formatted_projects = []
        for p in self.video_projects:
            project_copy = p.copy()
            project_copy["duration_str"] = self._format_duration(p["duration"])
            project_copy["clips"] = [
                {
                    **c,
                    "duration_str": f"{self._format_duration_str(c['start'])} - {self._format_duration_str(c['end'])}",
                }
                for c in p["clips"]
            ]
            formatted_projects.append(project_copy)
        return formatted_projects

    @rx.event
    def set_video_url(self, url: str):
        self.video_url = url
        self.error = None

    @rx.event(background=True)
    async def add_video(self):
        if not self.video_url:
            async with self:
                self.error = "Video URL cannot be empty."
            return
        async with self:
            self.is_loading = True
            self.error = None
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
            project_id = str(uuid.uuid4())
            new_project = Video(
                id=project_id,
                url=self.video_url,
                title=info.get("title", "Untitled Video"),
                thumbnail=info.get("thumbnail", "/placeholder.svg"),
                duration=info.get("duration", 0),
                duration_str="",
                status="pending",
                progress=0,
                file_path=None,
                error_message=None,
                segments=[],
                clips=[],
            )
            async with self:
                self.video_projects.insert(0, new_project)
                self.video_url = ""
                self.is_loading = False
            yield VideoState.download_video(project_id)
        except Exception as e:
            logging.exception(f"Error fetching video metadata: {e}")
            async with self:
                self.error = (
                    f"Failed to fetch video info. Please check the URL. Error: {str(e)}"
                )
                self.is_loading = False

    def _update_project_status(
        self,
        project_id: str,
        status: Status | None = None,
        progress: int | None = None,
        file_path: str | None = None,
        error_message: str | None = None,
        segments: list[TranscriptionSegment] | None = None,
        clips: list[Clip] | None = None,
    ):
        for i, proj in enumerate(self.video_projects):
            if proj["id"] == project_id:
                if status is not None:
                    self.video_projects[i]["status"] = status
                if progress is not None:
                    self.video_projects[i]["progress"] = progress
                if file_path is not None:
                    self.video_projects[i]["file_path"] = file_path
                if error_message is not None:
                    self.video_projects[i]["error_message"] = error_message
                if segments is not None:
                    self.video_projects[i]["segments"] = segments
                if clips is not None:
                    self.video_projects[i]["clips"] = clips
                break

    @rx.event
    def set_processing_video_id(self, video_id: str | None):
        self.processing_video_id = video_id

    @rx.event(background=True)
    async def download_video(self, project_id: str):
        async with self:
            self._update_project_status(project_id, "downloading", 0)
        project = next((p for p in self.video_projects if p["id"] == project_id), None)
        if not project:
            return
        upload_dir = rx.get_upload_dir() / "videos"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{project_id}.mp4"
        output_path = upload_dir / filename

        @rx.event
        def progress_hook(d):
            if d["status"] == "downloading":
                progress = int(d.get("_percent_str", "0%").replace("%", ""))
                self._update_project_status(project_id, "downloading", progress)
                yield

        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": str(output_path),
            "progress_hooks": [progress_hook],
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([project["url"]])
            async with self:
                self._update_project_status(
                    project_id, "complete", 100, file_path=f"videos/{filename}"
                )
                yield rx.toast.success(
                    f"Video '{project['title']}' downloaded successfully!"
                )
        except Exception as e:
            logging.exception(f"Download failed for {project['url']}: {e}")
            async with self:
                self._update_project_status(project_id, "error", error_message=str(e))
                yield rx.toast.error(f"Download failed: {str(e)}")