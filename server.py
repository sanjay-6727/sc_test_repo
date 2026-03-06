from fastapi import FastAPI, Request
from auth import get_installation_token, get_pr_files, comment_on_pr

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

        if action == "opened":

            print("Authenticating GitHub App...")

            token = get_installation_token(installation_id)

            print("Fetching PR files...")

            files = get_pr_files(repo, pr_number, token)

            print("Files changed:")
            for f in files:
                print("-", f["filename"])

            comment_on_pr(
                repo,
                pr_number,
                token,
                "🚀 **Stagecraft SDLC Agent** has started reviewing this PR."
            )

            print("Comment posted!")

    return {"status": "ok"}
