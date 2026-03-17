from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.tts_controller import router as tts_router

app = FastAPI(
    title="TTS Chapter Service",
    description="Convert webnovel chapters to WAV audio using voice cloning",
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(tts_router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "tts-chapter-service"}
