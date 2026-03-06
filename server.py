from fastapi import FastAPI, Request
from auth import get_installation_token, get_pr_files, comment_on_pr
from orchestrator.review_pipeline import run_stagecraft_review, build_report
import traceback

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        event = request.headers.get("X-GitHub-Event")

        print(f"\n===== WEBHOOK RECEIVED: {event} =====")

        if event == "pull_request":
            action = payload.get("action")
            repo = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            installation_id = payload["installation"]["id"]

            print(f"PR Action: {repr(action)}")
            print(f"Repo: {repo}")
            print(f"PR Number: {pr_number}")
            print(f"Installation ID: {installation_id}")

            # Trigger review on opened, reopened, or when new code is pushed (synchronize)
            if action in ["opened", "reopened", "synchronize"]:
                print(">>> Starting SDLC Review Process...")
                
                print("Authenticating GitHub App...")
                token = get_installation_token(installation_id)

                print("Fetching PR files...")
                files = get_pr_files(repo, pr_number, token)
                print(f"Found {len(files)} files changed.")

                print("Running multi-agent orchestration...")
                review_results = run_stagecraft_review(files)
                
                print("Generating report...")
                report = build_report(review_results)

                print("Posting comment to GitHub...")
                comment_on_pr(repo, pr_number, token, report)

                print("✅ Review posted successfully!")
            else:
                print(f"Ignoring PR action: {action}")

        return {"status": "ok"}
    
    except Exception as e:
        print("❌ ERROR in webhook handler:")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


