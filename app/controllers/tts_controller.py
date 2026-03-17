from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from dto import TTSChapterRequest, TTSChapterResponse, ErrorResponse
from app.services.tts_service import run_tts_chapter_workflow

router = APIRouter()


@router.post("/tts-clone-chapter", response_model=TTSChapterResponse)
async def tts_clone_chapter(
    story_base_url:  str        = Form(...),
    ref_audio:       UploadFile = File(...),
    chapter_start:   int        = Form(1),
    chapter_end:     int        = Form(10),
    ref_text:        str        = Form(""),
    temperature:     float      = Form(1.0),
    max_length:      int        = Form(200),
    split_long_text: bool       = Form(False),
) -> JSONResponse:

    filename = (ref_audio.filename or "").lower()
    if not (filename.endswith(".wav") or filename.endswith(".mp3")):
        raise HTTPException(status_code=400, detail=ErrorResponse(
            error=f"ref_audio phải là .wav hoặc .mp3, nhận được: '{ref_audio.filename}'"
        ).model_dump())

    try:
        req = TTSChapterRequest(
            story_base_url  = story_base_url,
            chapter_start   = chapter_start,
            chapter_end     = chapter_end,
            ref_text        = ref_text,
            temperature     = temperature,
            max_length      = max_length,
            split_long_text = split_long_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=ErrorResponse(error=str(e)).model_dump())

    ref_audio_bytes = await ref_audio.read()

    try:
        result = await run_tts_chapter_workflow(
            request         = req,
            ref_audio_bytes = ref_audio_bytes,
            ref_audio_name  = ref_audio.filename or "ref_audio.wav",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(error=str(e)).model_dump())

    return JSONResponse(content=result.model_dump(), status_code=200)
