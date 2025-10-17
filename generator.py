import os
import requests
import base64
import re
import time
import google.generativeai as genai

GITHUB_USER = os.getenv("GITHUB_USER", "")
GH_TOKEN = os.getenv("GH_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def safe_repo_name(task):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", task)[:80]

def github_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def create_repo_if_not_exists(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}"
    r = requests.get(url, headers=github_headers())
    if r.status_code == 200:
        return
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "private": False,
        "has_issues": False,
        "has_projects": False,
        "has_wiki": False,
        "auto_init": True,
        "license_template": "mit"
    }
    r = requests.post(url, headers=github_headers(), json=data)
    if r.status_code not in [201, 422]:
        raise Exception(f"Repo create failed: {r.text}")

def upload_file(repo_name, path, content_bytes, message):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/{path}"
    r = requests.get(url, headers=github_headers())
    sha = r.json()["sha"] if r.status_code == 200 else None
    data = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=github_headers(), json=data)
    if r.status_code not in [200, 201]:
        raise Exception(f"File upload failed: {r.text}")

def enable_github_pages(repo_name):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/pages"
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    r = requests.post(url, headers=github_headers(), json=data)
    if r.status_code not in [201, 409]:
        raise Exception(f"Failed to enable GitHub Pages: {r.text}")

def generate_app_code_with_gemini(brief, attachments=None):
    genai.configure(api_key=GEMINI_API_KEY)
    prompt = f"""You are an expert web developer. Write a minimal HTML+JS+CSS app that fulfills this brief:
{brief}
"""
    if attachments:
        prompt += "\nAttachments provided:\n"
        for att in attachments:
            prompt += f"- {att['name']}\n"
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def build_and_deploy(request_payload):
    task = request_payload["task"]
    brief = request_payload.get("brief", "")
    attachments = request_payload.get("attachments", [])
    repo_name = safe_repo_name(task)
    pages_url = f"https://{GITHUB_USER}.github.io/{repo_name}/"

    create_repo_if_not_exists(repo_name)

    # Use Gemini to generate index.html
    index_html = generate_app_code_with_gemini(brief, attachments)
    upload_file(repo_name, "index.html", index_html.encode("utf-8"), "Update index.html")

    # Professional README.md
    readme = f"""# Task App

## Summary
This project was generated automatically in response to the following brief:

> {brief}

The app is built using HTML, CSS, and JavaScript, and is designed to be minimal, functional, and easy to use.

## Setup
- No installation required.
- Visit the live site at: https://{GITHUB_USER}.github.io/{repo_name}/
- Or, download the repository and open `index.html` in your browser.

## Usage
- Follow the instructions on the web page.
- If the app supports file uploads or URL parameters, use them as described in the brief above.

## Code Explanation
- The main logic is in `index.html`, which contains all HTML, CSS, and JavaScript.
- The code was generated using Google Gemini LLM based on the provided brief.
- Attachments (if any) are included in the repository and referenced by the app as needed.

## License
This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
"""
    upload_file(repo_name, "README.md", readme.encode("utf-8"), "Update README.md")

    # .nojekyll
    upload_file(repo_name, ".nojekyll", b"", "Add .nojekyll")

    # Enable GitHub Pages
    enable_github_pages(repo_name)

    # Attachments
    for att in attachments or []:
        name = att.get("name", "attachment.bin")
        url = att.get("url", "")
        if url.startswith("data:"):
            _, b64 = url.split(",", 1)
            data_bytes = base64.b64decode(b64)
            upload_file(repo_name, name, data_bytes, f"Add {name}")

    time.sleep(5)
    repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}"
    commit_sha = "main"
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
