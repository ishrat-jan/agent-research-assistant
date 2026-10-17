from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Tell me one fun fact about space.",
)
print(response.text)