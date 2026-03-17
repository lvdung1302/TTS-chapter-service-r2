import re
import httpx
from bs4 import BeautifulSoup

from config import CRAWL_TIMEOUT, CRAWL_HEADERS, CRAWL_MAX_RETRIES


# ── URL builder ───────────────────────────────────────────────────────────────

def build_chapter_url(base_url: str, chapter_num: int) -> str:
    """
    Auto-detect URL pattern và build chapter URL.

    Pattern 1: .../chuong-N   → thay số cuối
    Pattern 2: .../chuong-    → append số
    Pattern 3: URL thường     → append /chuong-N/
    """
    base = base_url.rstrip("/")

    # Pattern 1: ends with chuong-N / chapter-N / tap-N
    if re.search(r"(?:chuong|chapter|chap|tap|ep)-\d+$", base, re.IGNORECASE):
        return re.sub(r"\d+$", str(chapter_num), base) + "/"

    # Pattern 2: ends with chuong- (no number yet)
    if re.search(r"(?:chuong|chapter|chap|tap|ep)-$", base, re.IGNORECASE):
        return f"{base}{chapter_num}/"

    # Pattern 3: plain story URL
    return f"{base}/chuong-{chapter_num}/"


def generate_chapter_urls(base_url: str, start: int, end: int) -> list[dict]:
    """Trả về list[{chapter_index, chapter_index_pad, chapter_url}]"""
    return [
        {
            "chapter_index":     i,
            "chapter_index_pad": str(i).zfill(2),
            "chapter_url":       build_chapter_url(base_url, i),
        }
        for i in range(start, end + 1)
    ]


# ── HTML selectors (webnovel.vn) ──────────────────────────────────────────────

_SELECTORS = {
    "title":        "#reader-title a",
    "chapter_name": ".reader__chapter",
    "content":      "#chapter-c",
}


def extract_chapter_html(html: str) -> dict:
    """
    Parse raw HTML và extract title / chapter_name / content
    theo CSS selector của webnovel.vn.
    """
    soup = BeautifulSoup(html, "html.parser")

    def _text(selector: str) -> str:
        el = soup.select_one(selector)
        return el.get_text(separator="\n", strip=True) if el else ""

    return {
        "title":        _text(_SELECTORS["title"]),
        "chapter_name": _text(_SELECTORS["chapter_name"]),
        "content":      _text(_SELECTORS["content"]),
    }


# ── HTTP crawl ────────────────────────────────────────────────────────────────

async def crawl_chapter(chapter_url: str) -> dict:
    """
    Crawl 1 chương từ chapter_url.
    Trả về: {status_code, title, chapter_name, content}
    Raises: httpx.HTTPError nếu không kết nối được
    """
    for attempt in range(1, CRAWL_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                headers=CRAWL_HEADERS,
                timeout=CRAWL_TIMEOUT,
                follow_redirects=True,
            ) as client:
                response = await client.get(chapter_url)

            if response.status_code >= 400:
                return {
                    "status_code": response.status_code,
                    "title":        "",
                    "chapter_name": "",
                    "content":      "",
                    "error":        f"HTTP {response.status_code}",
                }

            extracted = extract_chapter_html(response.text)
            return {"status_code": response.status_code, **extracted}

        except httpx.TimeoutException as e:
            if attempt == CRAWL_MAX_RETRIES:
                raise
            print(f"[Crawl] Timeout attempt {attempt}/{CRAWL_MAX_RETRIES}: {chapter_url}")

    # unreachable — just for type-checker
    raise RuntimeError("Crawl failed after retries")
