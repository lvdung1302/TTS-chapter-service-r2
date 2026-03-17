"""
local_storage.py
────────────────
Thay thế google_drive.py — lưu file WAV xuống local thay vì upload Drive.

Cấu trúc output:
  output/
  └── TTS_Session_20260316_221132/
      ├── Chương 1.wav
      ├── Chương 2.wav
      └── Chương 3.wav
"""

import os
from pathlib import Path

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))


# ── Session folder ────────────────────────────────────────────────────────────

def create_session_folder(session_name: str, **kwargs) -> dict:
    """
    Tạo folder local tại output/<session_name>/
    Trả về dict tương thích với interface cũ: {id, name, webViewLink}
    """
    folder_path = OUTPUT_DIR / session_name
    folder_path.mkdir(parents=True, exist_ok=True)

    abs_path = str(folder_path.resolve())
    print(f"📁 Created local folder: {abs_path}")

    return {
        "id":          abs_path,   # dùng path làm "id"
        "name":        session_name,
        "webViewLink": abs_path,
    }


# ── File save ─────────────────────────────────────────────────────────────────

def upload_audio(
    audio_bytes: bytes,
    filename:    str,
    folder_id:   str,   # ở đây folder_id chính là abs_path
    mime_type:   str = "audio/wav",
) -> dict:
    """
    Lưu audio_bytes vào folder_id/<filename>.
    Trả về dict tương thích: {id, name, webViewLink}
    """
    file_path = Path(folder_id) / filename
    file_path.write_bytes(audio_bytes)

    abs_path = str(file_path.resolve())
    print(f"💾 Saved: {abs_path}")

    return {
        "id":          abs_path,
        "name":        filename,
        "webViewLink": abs_path,
    }
