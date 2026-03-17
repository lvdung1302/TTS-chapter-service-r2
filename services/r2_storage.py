"""
r2_storage.py
─────────────
Upload file WAV lên Cloudflare R2.

File key format: /ten-truyen/Chuong 1.wav
Public URL:      https://<bucket>.r2.dev/ten-truyen/Chuong%201.wav
"""

import os
import boto3
from botocore.client import Config
from urllib.parse import quote

R2_ACCESS_KEY_ID     = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME       = os.getenv("R2_BUCKET_NAME", "")
R2_PUBLIC_URL        = os.getenv("R2_PUBLIC_URL", "")  # https://<bucket-hash>.r2.dev
R2_ENDPOINT          = os.getenv("R2_ENDPOINT", "")     # https://<account-id>.r2.cloudflarestorage.com

def _get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_audio_r2(
    audio_bytes: bytes,
    story_name:  str,
    filename:    str,
) -> dict:
    """
    Upload WAV lên R2.

    Args:
        audio_bytes: raw bytes của file WAV
        story_name:  tên truyện (slug từ URL) — dùng làm thư mục
        filename:    tên file .wav

    Returns:
        {
          "file_key": "/ten-truyen/Chuong 1.wav",
          "public_url": "https://xxx.r2.dev/ten-truyen/Chuong%201.wav"
        }
    """
    # ── Build file key: /story_name/filename ──────────────────────
    file_key = f"{story_name}/{filename}"

    client = _get_r2_client()
    client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=file_key,
        Body=audio_bytes,
        ContentType="audio/wav",
    )

    # ── Build public URL ──────────────────────────────────────────
    encoded_key = quote(file_key)   # encode spaces / ký tự đặc biệt
    base_url    = R2_PUBLIC_URL.rstrip("/")
    public_url  = f"{base_url}/{encoded_key}"

    print(f"☁️  R2 uploaded: {file_key} → {public_url}")

    return {
        "file_key":   f"/{file_key}",
        "public_url": public_url,
    }
