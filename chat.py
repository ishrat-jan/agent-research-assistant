from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
chat = client.chats.create(model = "gemini-flash-latest")

while True:
    q = input("You: ")
    if q == "quit":
        break
    print("AI:", chat.send_message(q).text)