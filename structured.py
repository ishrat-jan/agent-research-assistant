from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client()

class Topic(BaseModel):
    name: str
    why: str

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Give me 3 topics to study for AI engineer interviews.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Topic],
    ),
)

for topic in response.parsed:
    print(topic.name, "->", topic.why)