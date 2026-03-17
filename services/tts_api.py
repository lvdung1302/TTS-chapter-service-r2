import io
import zipfile
import httpx

from config import TTS_API_URL, TTS_API_TIMEOUT


async def call_tts_api(
    *,
    api_key:         str,
    ref_audio_bytes: bytes,
    ref_audio_name:  str,
    txt_content:     str,
    txt_filename:    str,
    ref_text:        str  = "",
    temperature:     float = 1.0,
    max_length:      int  = 200,
    split_long_text: bool = False,
) -> bytes:
    """
    Gửi ref_audio + txt_file lên TTS API.
    Trả về raw bytes của file .wav đầu tiên trong ZIP response.
    Raises: httpx.HTTPStatusError | ValueError
    """
    files = {
        "ref_audio": (ref_audio_name, ref_audio_bytes, _mime_for(ref_audio_name)),
        "files":     (txt_filename,   txt_content.encode("utf-8"), "text/plain"),
    }
    data = {
        "ref_text":        ref_text,
        "temperature":     str(temperature),
        "max_length":      str(max_length),
        "split_long_text": str(split_long_text).lower(),
    }
    headers = {
        "x-api-key": api_key,
        "accept":    "application/json",
    }

    async with httpx.AsyncClient(timeout=TTS_API_TIMEOUT) as client:
        response = await client.post(
            TTS_API_URL,
            headers=headers,
            data=data,
            files=files,
        )
        response.raise_for_status()

    return _extract_wav_from_zip(response.content)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mime_for(filename: str) -> str:
    if filename.lower().endswith(".mp3"):
        return "audio/mpeg"
    return "audio/wav"


def _extract_wav_from_zip(zip_bytes: bytes) -> bytes:
    """
    Giải nén ZIP và trả về bytes của .wav đầu tiên.
    Raises: ValueError nếu không tìm thấy .wav trong ZIP.
    """
    if not zip_bytes:
        raise ValueError("TTS API trả về response rỗng.")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        wav_names = [n for n in zf.namelist() if n.lower().endswith(".wav")]
        if not wav_names:
            raise ValueError(
                f"Không tìm thấy .wav trong ZIP. "
                f"Nội dung: {zf.namelist()}"
            )
        with zf.open(wav_names[0]) as f:
            return f.read()
