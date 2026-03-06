from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    print("\n===== WEBHOOK RECEIVED =====")
    print("Event:", event)

    if event == "pull_request":
        action = payload["action"]
        repo = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        installation_id = payload["installation"]["id"]

        print("PR Action:", action)
        print("Repo:", repo)
        print("PR Number:", pr_number)
        print("Installation ID:", installation_id)

    return {"status": "ok"} 
