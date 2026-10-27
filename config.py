import logging

MODEL = "gemini-3.5-flash"
MAX_STEPS = 8
MAX_TOOL_CHARS = 8000
HEADERS = {"User-Agent": "agent-research-assistant/0.1 (learning project)"}

SYSTEM = (
    "You are a research assistant that answers using research papers. "
    "Use search_papers at most 2 times. "
    "Use fetch_paper_text on at most 1 paper, and only when the abstract is not enough "
    "or the user asks for details. "
    "Always include each paper's link. "
    "Never invent papers or facts. If the results are not a good match, say so, "
    "and summarise the closest ones."
)

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)