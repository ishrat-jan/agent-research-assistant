from agent import run_agent

print("Research assistant. Type quit to stop.")
while True:
    q = input("\nYou: ").strip()
    if q.lower() == "quit":
        break
    if not q:
        continue
    print("\nAI:", run_agent(q))