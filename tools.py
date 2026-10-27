import io
import time
import requests
import xml.etree.ElementTree as ET
from datetime import date
from pypdf import PdfReader
from config import HEADERS, MAX_TOOL_CHARS


def get_current_date() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


def _from_arxiv(query, n):
    r = requests.get(
        "https://export.arxiv.org/api/query",
        params={"search_query": f"all:{query}", "max_results": n},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(r.text).findall("a:entry", ns):
        title = e.find("a:title", ns).text.strip().replace("\n", " ")
        link = e.find("a:id", ns).text.strip()
        summary = e.find("a:summary", ns).text.strip().replace("\n", " ")[:500]
        out.append(f"Title: {title}\nLink: {link}\nAbstract: {summary}")
    return out


def _from_semantic_scholar(query, n):
    r = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": query, "limit": n, "fields": "title,abstract,year,url"},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    out = []
    for p in r.json().get("data", []):
        abstract = (p.get("abstract") or "No abstract available.")[:500]
        out.append(
            f"Title: {p.get('title')}\nYear: {p.get('year')}\n"
            f"Link: {p.get('url')}\nAbstract: {abstract}"
        )
    return out


def search_papers(query: str, max_results: int = 3) -> str:
    """Search research papers. Tries arXiv first, then Semantic Scholar.
    Returns title, link and abstract for each paper."""
    n = max(1, min(int(max_results), 5))
    problems = []
    for name, fn in [("arXiv", _from_arxiv), ("Semantic Scholar", _from_semantic_scholar)]:
        try:
            papers = fn(query, n)
            if papers:
                return f"Source: {name}\n\n" + "\n\n".join(papers)
            problems.append(f"{name}: no results")
        except requests.RequestException as e:
            problems.append(f"{name}: {e}")
        time.sleep(1)
    return "Search failed. " + " | ".join(problems)


def fetch_paper_text(arxiv_id: str, max_pages: int = 3) -> str:
    """Download an arXiv paper's PDF and return the text of its first pages.
    arxiv_id can be like 2206.10552 or a full arxiv.org link."""
    paper_id = arxiv_id.split("/abs/")[-1].split("/pdf/")[-1].replace(".pdf", "").strip()
    try:
        r = requests.get(f"https://arxiv.org/pdf/{paper_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        reader = PdfReader(io.BytesIO(r.content))
    except Exception as e:
        return f"Could not read paper {paper_id}: {e}"
    pages = reader.pages[: max(1, min(int(max_pages), 5))]
    text = "\n".join(page.extract_text() or "" for page in pages)
    return text[:MAX_TOOL_CHARS] or "No text could be extracted."


TOOLS = {
    "get_current_date": get_current_date,
    "search_papers": search_papers,
    "fetch_paper_text": fetch_paper_text,
}