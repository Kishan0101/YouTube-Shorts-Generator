# YouTube to Shorts Converter - Project Plan

## Phase 1: Core Infrastructure & Video Download ✅
- [x] Set up project structure with proper state management
- [x] Implement YouTube video download functionality (yt_dlp integration)
- [x] Create upload interface with video link input and validation
- [x] Build video metadata extraction (duration, title, thumbnail)
- [x] Add progress tracking for download operations

---

## Phase 2: Audio Analysis & Segment Detection ✅
- [x] Integrate speech recognition for audio transcription (whisper)
- [x] Implement sentiment analysis on transcribed text (textblob)
- [x] Build engagement scoring algorithm (keyword density, sentiment peaks)
- [x] Create segment detection logic (15-60 sec clips)
- [x] Display detected segments with timestamps and scores in dashboard

---

## Phase 3: Enhanced Scoring & Cookie Support ✅
- [x] Add cookie support for gated YouTube videos (--cookies-from-browser or cookies file)
- [x] Implement loudness analysis for audio segments (pydub AudioSegment)
- [x] Enhance scoring algorithm: loudness + sentiment + keyword density
- [x] Add configurable scoring weights (UI sliders)
- [x] Re-rank segments based on enhanced multi-factor scoring

---

## Phase 4: Video Processing & Clip Generation with Effects ⏳
- [ ] Implement video clipping with moviepy (extract segments)
- [ ] Auto-generate captions with whisper and burn into video with styled text
- [ ] Convert to 9:16 aspect ratio with intelligent safe crop (face detection or center-weighted)
- [ ] Add background music integration with volume mixing and ducking
- [ ] Overlay branding (logo watermark) with position/opacity controls
- [ ] Add processing status tracking (generating, rendering, complete)
- [ ] Generate downloadable shorts with proper export settings

---

## Phase 5: Dashboard Enhancement & Clip Management
- [ ] Build clip preview player with video.js or custom HTML5 player
- [ ] Add segment timeline visualization with waveform
- [ ] Implement manual segment re-selection (drag handles to adjust start/end)
- [ ] Create style editor panel (music selection, watermark position, caption style)
- [ ] Add clip comparison view (side-by-side preview)
- [ ] Build export queue with batch processing support

---

## Phase 6: Advanced Features & Polish
- [ ] Add template system for branding (multiple logo/watermark options)
- [ ] Implement custom clip editing (adjust start/end times manually)
- [ ] Create analytics view (engagement scores, clip performance predictions)
- [ ] Add batch processing for multiple videos
- [ ] Implement export settings (quality, format, resolution options)
- [ ] Polish UI with animations, loading states, and error handling
