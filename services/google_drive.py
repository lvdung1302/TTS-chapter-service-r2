"""
local_storage (replaces google_drive.py)
─────────────────────────────────────────
Lưu file WAV xuống local thay vì Google Drive.
Output folder: ./output/<session_name>/
"""

from pathlib import Path

OUTPUT_ROOT = Path("output")


def create_session_folder(session_name: str, **kwargs) -> dict:
    folder_path = OUTPUT_ROOT / session_name
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created local folder: {folder_path.resolve()}")
    return {
        "id":          str(folder_path.resolve()),
        "name":        session_name,
        "webViewLink": str(folder_path.resolve()),
    }


def upload_audio(
    audio_bytes: bytes,
    filename:    str,
    folder_id:   str,
    mime_type:   str = "audio/wav",
) -> dict:
    file_path = Path(folder_id) / filename
    file_path.write_bytes(audio_bytes)
    print(f"💾 Saved: {file_path}")
    return {
        "id":          str(file_path),
        "name":        filename,
        "webViewLink": str(file_path),
    }
