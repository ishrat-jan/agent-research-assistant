import time
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
import config
from tools import TOOLS

load_dotenv()
client = genai.Client()
log = logging.getLogger("agent")

gen_config = types.GenerateContentConfig(
    system_instruction=config.SYSTEM,
    tools=list(TOOLS.values()),
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def show(message):
    print(message)
    log.info(message)


def generate_with_retry(contents):
    for attempt in range(5):
        try:
            return client.models.generate_content(
                model=config.MODEL, contents=contents, config=gen_config
            )
        except errors.APIError as e:
            if e.code in (429, 500, 503, 504) and attempt < 4:
                wait = 5 * 2 ** attempt
                show(f"   Gemini error {e.code}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def call_tool(name, args):
    func = TOOLS.get(name)
    if func is None:
        return f"Unknown tool: {name}"
    try:
        return func(**args)
    except Exception as e:
        return f"Tool {name} failed: {e}"


def run_agent(question):
    log.info("QUESTION: %s", question)
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]
    for step in range(config.MAX_STEPS):
        response = generate_with_retry(contents)
        calls = response.function_calls
        if not calls:
            log.info("ANSWER: %s", response.text)
            return response.text
        contents.append(response.candidates[0].content)
        parts = []
        for call in calls:
            show(f"Step {step + 1}: calling {call.name} with {call.args}")
            result = call_tool(call.name, call.args)
            show(f"   result: {len(str(result))} characters")
            if str(result).startswith(("Search failed", "Could not", "Tool ", "Unknown tool")):
                log.warning("TOOL PROBLEM: %s", result)
                print("   ERROR:", result)
            parts.append(types.Part.from_function_response(
                name=call.name, response={"result": result}
            ))
        contents.append(types.Content(role="user", parts=parts))
    return "Stopped: too many steps."