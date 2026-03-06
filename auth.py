import jwt
import time
import requests

# ============================
# CONFIG
# ============================

APP_ID = "3024195"   # e.g. 1234567
PRIVATE_KEY_PATH = "stagecraft-sdlc-agent.2026-03-06.private-key.pem"


# ============================
# LOAD PRIVATE KEY
# ============================

with open(PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()


# ============================
# GENERATE APP JWT
# ============================

def generate_jwt():
    """
    Generates a JWT for GitHub App authentication.
    """

    payload = {
        "iat": int(time.time()),           # issued at
        "exp": int(time.time()) + 600,     # expires in 10 minutes
        "iss": APP_ID                      # GitHub App ID
    }

    encoded_jwt = jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm="RS256"
    )

    return encoded_jwt


# ============================
# GET INSTALLATION TOKEN
# ============================

def get_installation_token(installation_id):
    """
    Exchanges the GitHub App JWT for an installation access token.
    """

    jwt_token = generate_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Failed to get installation token: {response.text}")

    return response.json()["token"]


# ============================
# FETCH PR FILES
# ============================

def get_pr_files(repo_full_name, pr_number, token):
    """
    Fetches files changed in a pull request.
    """

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {response.text}")

    return response.json()


# ============================
# COMMENT ON PR
# ============================

def comment_on_pr(repo_full_name, pr_number, token, message):
    """
    Posts a comment on the pull request.
    """

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    data = {
        "body": message
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 201:
        raise Exception(f"Failed to comment on PR: {response.text}")

    return response.json()