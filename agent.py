import time
import requests
import xml.etree.ElementTree as ET
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.5-flash"
MAX_STEPS = 8
HEADERS = {"User-Agent": "agent-research-assistant/0.1 (learning project)"}

SYSTEM = (
    "You are a research assistant. Use search_papers at most 2 times. "
    "If the results are not a perfect match, summarise the closest ones and say so. "
    "Always include each paper's link."
)


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


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


TOOLS = {
    "add": add,
    "get_current_date": get_current_date,
    "search_papers": search_papers,
}

config = types.GenerateContentConfig(
    system_instruction=SYSTEM,
    tools=[add, get_current_date, search_papers],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def generate_with_retry(contents):
    for attempt in range(5):
        try:
            return client.models.generate_content(
                model=MODEL, contents=contents, config=config
            )
        except errors.APIError as e:
            if e.code in (429, 500, 503, 504) and attempt < 4:
                wait = 5 * 2 ** attempt
                print(f"   Gemini error {e.code}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def run_agent(question):
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]
    for step in range(MAX_STEPS):
        response = generate_with_retry(contents)
        calls = response.function_calls
        if not calls:
            return response.text
        contents.append(response.candidates[0].content)
        parts = []
        for call in calls:
            print(f"Step {step + 1}: calling {call.name} with {call.args}")
            result = TOOLS[call.name](**call.args)
            print(f"   result: {len(str(result))} characters")
            if str(result).startswith("Search failed"):
                print("   ERROR:", result)
            elif str(result).startswith("Source:"):
                print("  ", str(result).splitlines()[0])
            parts.append(types.Part.from_function_response(
                name=call.name, response={"result": result}
            ))
        contents.append(types.Content(role="user", parts=parts))
    return "Stopped: too many steps."


print(run_agent("Find 3 recent papers on vision transformers for crop monitoring and summarise each in one line."))