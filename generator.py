import os
import subprocess
import tempfile
import pathlib
import base64
import shutil
import time
import requests
import re

GITHUB_USER = os.getenv("GITHUB_USER", "")
GH_TOKEN = os.getenv("GH_TOKEN", "")
DEFAULT_BRANCH = "main"

def sh(cmd, cwd=None):
    return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True).strip()

def safe_repo_name(task):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", task)[:80]

def write_static_app(workdir, brief, attachments):
    www = pathlib.Path(workdir, "site")
    www.mkdir(parents=True, exist_ok=True)
    # Decode attachments into the repo
    for att in attachments or []:
        name = att.get("name", "attachment.bin")
        url = att.get("url", "")
        if url.startswith("data:"):
            header, b64 = url.split(",", 1)
            data = base64.b64decode(b64)
            pathlib.Path(www, name).write_bytes(data)
    # Minimal static page
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
    (www / "index.html").write_text(index_html, encoding="utf-8")
    readme = f"# Task App\n\nBrief: {brief}\n\nThis app is auto-generated.\n"
    (pathlib.Path(workdir) / "README.md").write_text(readme, encoding="utf-8")
    return www

def build_and_deploy(request_payload):
    email = request_payload["email"]
    task = request_payload["task"]
    brief = request_payload.get("brief", "")
    attachments = request_payload.get("attachments", [])
    repo_name = safe_repo_name(task)
    pages_url = f"https://{GITHUB_USER}.github.io/{repo_name}/"
    with tempfile.TemporaryDirectory() as td:
        sh("git init -b main", cwd=td)
        write_static_app(td, brief, attachments)
        # Create repo if not exists
        try:
            sh(f'gh repo view {repo_name}', cwd=td)
        except subprocess.CalledProcessError:
            sh(f'gh repo create {repo_name} --public -l MIT -y', cwd=td)
        # Move site files to root
        site = pathlib.Path(td, "site")
        for p in site.iterdir():
            shutil.move(str(p), str(pathlib.Path(td, p.name)))
        shutil.rmtree(site)
        pathlib.Path(td, ".nojekyll").write_text("", encoding="utf-8")
        sh('git add .', cwd=td)
        sh('git commit -m "Update app"', cwd=td)
        sh('git push -u origin main', cwd=td)
        time.sleep(5)
        repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}"
        commit_sha = sh("git rev-parse HEAD", cwd=td)
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
