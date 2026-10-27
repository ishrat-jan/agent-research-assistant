from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

config = types.GenerateContentConfig(
    tools=[add],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

question = "What is 1234 plus 5678?"
response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents=question,
    config=config,
)

call = response.function_calls[0]
print("Model wants:", call.name, call.args)

result = add(**call.args)

contents = [
    types.Content(role="user", parts=[types.Part(text=question)]),
    response.candidates[0].content,
    types.Content(role="user", parts=[
        types.Part.from_function_response(name=call.name, response={"result": result})
    ]),
]
final = client.models.generate_content(
    model="gemini-flash-latest",
    contents=contents,
    config=config,
)
print("Final answer:", final.text)