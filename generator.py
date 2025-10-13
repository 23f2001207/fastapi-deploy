import os
import requests
import base64
import re
import time

GITHUB_USER = os.getenv("GITHUB_USER", "")
GH_TOKEN = os.getenv("GH_TOKEN", "")

def safe_repo_name(task):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", task)[:80]

def github_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def create_repo_if_not_exists(repo_name):
    # Check if repo exists
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}"
    r = requests.get(url, headers=github_headers())
    if r.status_code == 200:
        return
    # Create repo
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit"
    }
    r = requests.post(url, headers=github_headers(), json=data)
    if r.status_code not in [201, 422]:  # 422 = already exists
        raise Exception(f"Repo create failed: {r.text}")

def upload_file(repo_name, path, content, message):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/{path}"
    # Check if file exists to get sha
    r = requests.get(url, headers=github_headers())
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        sha = None
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=github_headers(), json=data)
    if r.status_code not in [200, 201]:
        raise Exception(f"File upload failed: {r.text}")

def build_and_deploy(request_payload):
    task = request_payload["task"]
    brief = request_payload.get("brief", "")
    attachments = request_payload.get("attachments", [])
    repo_name = safe_repo_name(task)
    pages_url = f"https://{GITHUB_USER}.github.io/{repo_name}/"

    create_repo_if_not_exists(repo_name)

    # index.html
    index_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Task App</title>
</head>
<body>
<h1>Task App</h1>
<p>{brief}</p>
</body>
</html>
"""
    upload_file(repo_name, "index.html", index_html, "Update index.html")

    # README.md
    readme = f"# Task App\n\nBrief: {brief}\n\nThis app is auto-generated.\n"
    upload_file(repo_name, "README.md", readme, "Update README.md")

    # .nojekyll
    upload_file(repo_name, ".nojekyll", "", "Add .nojekyll")

    # MIT License (optional, since auto_init with mit license)
    # upload_file(repo_name, "LICENSE", mit_license_text, "Add MIT License")

    # Attachments
    for att in attachments or []:
        name = att.get("name", "attachment.bin")
        url = att.get("url", "")
        if url.startswith("data:"):
            header, b64 = url.split(",", 1)
            data = base64.b64decode(b64)
            upload_file(repo_name, name, data.decode("utf-8"), f"Add {name}")

    # Wait for GitHub Pages to deploy (first time can take a few minutes)
    time.sleep(5)
    repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}"
    commit_sha = "main"  # Not strictly needed for API-based push
    return {"repo_url": repo_url, "commit_sha": commit_sha, "pages_url": pages_url}

def post_evaluation(request_payload, result):
    data = {
        "email": request_payload["email"],
        "task": request_payload["task"],
        "round": request_payload.get("round", 1),
        "nonce": request_payload["nonce"],
        "repo_url": result["repo_url"],
        "commit_sha": result["commit_sha"],
        "pages_url": result["pages_url"],
    }
    url = request_payload["evaluation_url"]
    delay = 1
    for _ in range(6):
        try:
            r = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(delay)
        delay = min(delay * 2, 60)
