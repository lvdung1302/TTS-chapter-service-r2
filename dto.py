from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from config import MAX_CHAPTERS_PER_REQUEST


# ── Request ───────────────────────────────────────────────────────────────────

class TTSChapterRequest(BaseModel):
    story_base_url:  str
    chapter_start:   int           = 1
    chapter_end:     int           = 10
    ref_text:        Optional[str] = ""
    temperature:     float         = 1.0
    max_length:      int           = 200
    split_long_text: bool          = False

    @field_validator("story_base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("http"):
            raise ValueError(
                f"story_base_url không hợp lệ: '{v}'. "
                "Phải bắt đầu bằng http hoặc https."
            )
        return v

    @model_validator(mode="after")
    def validate_chapter_range(self) -> "TTSChapterRequest":
        if self.chapter_start < 1:
            self.chapter_start = 1
        if self.chapter_end < self.chapter_start:
            self.chapter_end = self.chapter_start
        total = self.chapter_end - self.chapter_start + 1
        if total > MAX_CHAPTERS_PER_REQUEST:
            raise ValueError(
                f"Tối đa {MAX_CHAPTERS_PER_REQUEST} chương mỗi lần. "
                f"Bạn yêu cầu {total} chương ({self.chapter_start}→{self.chapter_end})."
            )
        return self


# ── Internal ──────────────────────────────────────────────────────────────────

class SessionContext(BaseModel):
    session_name:     str
    timestamp:        str
    folder_id:        str
    folder_name:      str
    drive_folder_url: str
    api_key:          str
    ref_text:         str
    temperature:      float
    max_length:       int
    split_long_text:  bool
    chapter_total:    int


# ── Response ──────────────────────────────────────────────────────────────────

class AudioFile(BaseModel):
    name:       str
    file_key:   str   # /ten-truyen/Chuong 1.wav  — dùng để backend gọi
    public_url: str   # https://xxx.r2.dev/ten-truyen/Chuong%201.wav


class TTSChapterResponse(BaseModel):
    success:           bool
    session_name:      str
    story_name:        str
    chapter_total:     int
    audio_files_count: int
    audio_files:       list[AudioFile]


class ErrorResponse(BaseModel):
    success:     bool = False
    error:       str
    chapter_url: str  = ""
