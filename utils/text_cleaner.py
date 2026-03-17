import re


# ── Noise patterns to remove ──────────────────────────────────────────────────

_NOISE_PATTERNS = [
    r"Chương trước|Chương tiếp|Mục lục|Danh sách chương",
    r"\bAD FILL\b|advertisement",
    r"https?://\S+",
]
_NOISE_RE = re.compile("|".join(_NOISE_PATTERNS), re.IGNORECASE)

_SAFE_FILENAME_RE = re.compile(r'[\\/:*?"<>|]')
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


# ── Public API ────────────────────────────────────────────────────────────────

def clean_content(raw: str) -> str:
    """Loại bỏ noise, chuẩn hoá khoảng trắng."""
    text = _NOISE_RE.sub("", raw)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def build_txt_filename(chapter_name: str, chapter_pad: str) -> str:
    """
    Tạo tên file .txt từ chapter_name.
    Fallback về chapter_XX.txt nếu tên rỗng hoặc không an toàn.
    """
    safe = _SAFE_FILENAME_RE.sub("", chapter_name)
    safe = re.sub(r"\s+", " ", safe).strip()
    return f"{safe}.txt" if safe else f"chapter_{chapter_pad}.txt"


def is_valid_content(content: str, min_length: int = 10) -> bool:
    return bool(content) and len(content) >= min_length
