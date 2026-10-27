import io
import requests
from pypdf import PdfReader

HEADERS = {"User-Agent": "agent-research-assistant/0.1 (learning project)"}


def fetch_paper_text(arxiv_id: str, max_pages: int = 3) -> str:
    """Download an arXiv paper's PDF and return the text of its first pages."""
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        reader = PdfReader(io.BytesIO(r.content))
    except Exception as e:
        return f"Could not read paper {arxiv_id}: {e}"
    pages = reader.pages[:max_pages]
    return "\n".join(page.extract_text() or "" for page in pages)


text = fetch_paper_text("2206.10552")
print(len(text), "characters")
print(text[:600])