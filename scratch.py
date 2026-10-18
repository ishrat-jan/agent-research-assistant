from dotenv import load_dotenv
load_dotenv()

from google import genai
client = genai.Client()
response = client.models.generate_content(
    model = "gemini-flash-latest",
    contents = "tell me about moon",
)
print(response.text)