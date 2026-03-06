from fastapi import FastAPI, Request
from auth import get_installation_token, get_pr_files, comment_on_pr
from orchestrator.review_pipeline import run_stagecraft_review, build_report

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

            print(f"Analyzing {len(files)} files with Multi-Agent Orchestrator...")
            
            # Run the multi-agent review pipeline
            review_results = run_stagecraft_review(files)
            
            # Build the aggregated report
            report = build_report(review_results)

            print("Posting review report to GitHub...")
            comment_on_pr(repo, pr_number, token, report)

            print("Review posted successfully!")

    return {"status": "ok"}

