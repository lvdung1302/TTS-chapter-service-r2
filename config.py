import os
from dotenv import load_dotenv

load_dotenv()

# ── TTS API ──────────────────────────────────────────────────────────────────
TTS_API_KEY = os.getenv("TTS_API_KEY", "peaky7blinders0on1my2mindkey7012")
TTS_API_URL = os.getenv("TTS_API_URL", "http://76.13.193.175:8000/v1/text-to-speech/clone/files")
TTS_API_TIMEOUT = int(os.getenv("TTS_API_TIMEOUT", "1000"))  # seconds

# ── Google Drive ─────────────────────────────────────────────────────────────
GOOGLE_DRIVE_PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "1IBqr-ieFPPIJqRwZCM4TA6S3kqXOZIWO")
GOOGLE_SERVICE_ACCOUNT_FILE   = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

# ── Crawler ───────────────────────────────────────────────────────────────────
CRAWL_TIMEOUT     = int(os.getenv("CRAWL_TIMEOUT", "30"))   # seconds
CRAWL_MAX_RETRIES = int(os.getenv("CRAWL_MAX_RETRIES", "3"))
CRAWL_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9",
}

# ── Validation limits ─────────────────────────────────────────────────────────
MAX_CHAPTERS_PER_REQUEST = int(os.getenv("MAX_CHAPTERS_PER_REQUEST", "50"))
