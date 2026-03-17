import asyncio
from datetime import datetime

from dto import (
    TTSChapterRequest,
    SessionContext,
    AudioFile,
    TTSChapterResponse,
)
from config import TTS_API_KEY
from services.r2_storage import upload_audio_r2
from services.tts_api import call_tts_api
from utils.crawler import generate_chapter_urls, crawl_chapter
from utils.text_cleaner import clean_content, build_txt_filename, is_valid_content


async def run_tts_chapter_workflow(
    request:         TTSChapterRequest,
    ref_audio_bytes: bytes,
    ref_audio_name:  str,
) -> TTSChapterResponse:

    # 1. Build session
    session = _build_session(request)
    print(f"🚀 Session: {session.session_name} | {session.chapter_total} chapters")

    # 2. Generate chapter URLs
    chapter_items = generate_chapter_urls(
        base_url=request.story_base_url,
        start=request.chapter_start,
        end=request.chapter_end,
    )
    print(f"📝 Generated {len(chapter_items)} chapter URLs")

    # 3. Process từng chương (concurrent)
    tasks = [
        _process_one_chapter(item, session, ref_audio_bytes, ref_audio_name)
        for item in chapter_items
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    audio_files = sorted(
        [r for r in results if r is not None],
        key=lambda f: f.file_key,
    )

    print(f"✅ {len(audio_files)}/{len(chapter_items)} chapters uploaded to R2")

    return TTSChapterResponse(
        success           = True,
        session_name      = session.session_name,
        story_name        = session.session_name,
        chapter_total     = session.chapter_total,
        audio_files_count = len(audio_files),
        audio_files       = audio_files,
    )


async def _process_one_chapter(
    item:            dict,
    session:         SessionContext,
    ref_audio_bytes: bytes,
    ref_audio_name:  str,
) -> AudioFile | None:
    chapter_index = item["chapter_index"]
    chapter_pad   = item["chapter_index_pad"]
    chapter_url   = item["chapter_url"]

    try:
        # Crawl
        print(f"🌐 Crawling chapter {chapter_index}: {chapter_url}")
        crawl_result = await crawl_chapter(chapter_url)

        if crawl_result["status_code"] >= 400:
            print(f"[Skip] Chapter {chapter_index}: HTTP {crawl_result['status_code']}")
            return None

        # Extract & clean
        chapter_name = crawl_result.get("chapter_name", f"Chương {chapter_index}").strip()
        raw_content  = crawl_result.get("content", "").strip()
        content      = clean_content(raw_content)

        if not is_valid_content(content):
            print(f"[Skip] Chapter {chapter_index}: empty content")
            return None

        txt_name = build_txt_filename(chapter_name, chapter_pad)
        wav_name = txt_name.replace(".txt", ".wav")
        print(f"📄 Chapter {chapter_index} | \"{chapter_name}\" | {len(content)} chars")

        # TTS API
        wav_bytes = await call_tts_api(
            api_key         = session.api_key,
            ref_audio_bytes = ref_audio_bytes,
            ref_audio_name  = ref_audio_name,
            txt_content     = content,
            txt_filename    = txt_name,
            ref_text        = session.ref_text,
            temperature     = session.temperature,
            max_length      = session.max_length,
            split_long_text = session.split_long_text,
        )

        # Upload R2 (không lưu local)
        r2_result = upload_audio_r2(
            audio_bytes = wav_bytes,
            story_name  = session.session_name,
            filename    = wav_name,
        )

        return AudioFile(
            name       = wav_name,
            file_key   = r2_result["file_key"],
            public_url = r2_result["public_url"],
        )

    except Exception as e:
        print(f"[Error] Chapter {chapter_index} ({chapter_url}): {e}")
        return None


def _extract_story_name(url: str) -> str:
    import re
    from urllib.parse import urlparse
    parts = [p for p in urlparse(url).path.strip("/").split("/") if p]
    story_parts = [
        p for p in parts
        if not re.match(r"(?:chuong|chapter|chap|tap|ep)-?\d*$", p, re.IGNORECASE)
    ]
    return story_parts[0] if story_parts else f"TTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _build_session(request: TTSChapterRequest) -> SessionContext:
    now        = datetime.now()
    ts         = now.strftime("%Y%m%d_%H%M%S")
    story_name = _extract_story_name(request.story_base_url)
    return SessionContext(
        session_name     = story_name,
        timestamp        = ts,
        folder_id        = "",
        folder_name      = "",
        drive_folder_url = "",
        api_key          = TTS_API_KEY,
        ref_text         = request.ref_text or "",
        temperature      = request.temperature,
        max_length       = request.max_length,
        split_long_text  = request.split_long_text,
        chapter_total    = request.chapter_end - request.chapter_start + 1,
    )
