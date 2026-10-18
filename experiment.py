from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

instructions = [
    "You are a strict professor. Be formal and precise.",
    "Explain like I am 10 years old.",
    "Answer in exactly two lines.",
]
temperatures = [0.0, 0.7, 1.5]

for inst in instructions:
    for temp in temperatures:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents="What is a vision transformer?",
            config=types.GenerateContentConfig(
                system_instruction=inst,
                temperature=temp,
            ),
        )
        print("INSTRUCTION:", inst)
        print("TEMPERATURE:", temp)
        print(response.text)
        print("-" * 40)