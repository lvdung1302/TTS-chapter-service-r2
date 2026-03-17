# TTS Chapter Service

Chuyển đổi chương truyện web → file WAV bằng voice cloning.

## Cấu trúc

```
tts-chapter-service/
├── app/
│   ├── controllers/
│   │   └── tts_controller.py   # FastAPI route: POST /v1/tts-clone-chapter
│   ├── services/
│   │   └── tts_service.py      # Orchestration — toàn bộ pipeline
│   └── main.py                 # Entry point
├── services/
│   ├── tts_api.py              # Gọi TTS API → nhận ZIP → extract WAV
│   └── local_storage.py        # Lưu WAV xuống local output/
├── utils/
│   ├── crawler.py              # HTTP crawl + HTML extraction (BeautifulSoup)
│   └── text_cleaner.py         # Clean content + build filename
├── config.py                   # Đọc biến môi trường từ .env
├── dto.py                      # Pydantic models (Request / Response)
├── pyproject.toml              # Dependencies
├── Dockerfile
├── .env.example
└── .gitignore
```

## Cài đặt

```bash
# 1. Tạo và kích hoạt venv
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2. Cài dependencies
pip install -e .

# 3. Tạo file .env
cp .env.example .env
# → Điền TTS_API_KEY và các biến cần thiết
```

## Chạy server

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## API

### `POST /v1/tts-clone-chapter`

**Content-Type:** `multipart/form-data`

| Field | Type | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `story_base_url` | string | ✅ | — | URL truyện |
| `ref_audio` | file | ✅ | — | Giọng mẫu `.wav`/`.mp3` |
| `chapter_start` | int | | 1 | Chương bắt đầu |
| `chapter_end` | int | | 10 | Chương kết thúc (tối đa 50) |
| `ref_text` | string | | "" | Text tham chiếu |
| `temperature` | float | | 1.0 | Temperature TTS |
| `max_length` | int | | 200 | Max length per chunk |
| `split_long_text` | bool | | false | Tách đoạn dài |

**Response:**
```json
{
  "success": true,
  "session_name": "TTS_Session_20260316_221132",
  "folder_name": "TTS_Session_20260316_221132",
  "output_folder": "D:\\...\\output\\TTS_Session_20260316_221132",
  "chapter_total": 3,
  "audio_files_count": 3,
  "audio_files": [
    { "name": "Chương 1.wav", "local_path": "D:\\...\\Chương 1.wav" }
  ]
}
```

Output WAV được lưu tại `output/TTS_Session_<timestamp>/`.
