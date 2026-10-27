from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1),
    )
)

names = []
for m in client.models.list():
    name = m.name.replace("models/", "")
    actions = m.supported_actions or []
    if "generateContent" in actions and "gemini" in name and ("flash" in name or "lite" in name):
        names.append(name)

names = names[:15]
print(len(names), "models to test")
for name in names:
    try:
        client.models.generate_content(model=name, contents="Say hi")
        print("OK     ", name)
    except Exception as e:
        print("FAILED ", name, str(e)[:70])