# 🤖 LLM Code Deployment Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)


**Roll No:** 23f2001207  
**GitHub:** [@23f2001207](https://github.com/23f2001207)

***

## 📌 Overview

This project implements an *automated developer agent* that receives natural-language app specifications, generates working web applications using a Large Language Model (LLM), deploys them to GitHub Pages, and reports deployment metadata for automated evaluation.

Built with **FastAPI**, this service fulfills the requirements of the *TDS Project 1 - LLM Code Deployment Assignment* by handling both **Round 1 (Build)** and **Round 2 (Revise)** tasks end-to-end.

***

## 🚀 What Does It Do?

Given a JSON task request like:
```json
{
  "email": "student@example.com",
  "secret": "your-secret",
  "task": "captcha-solver-abc12",
  "round": 1,
  "brief": "Create a captcha solver that handles ?url=...",
  "evaluation_url": "https://eval.example.com/notify",
  "attachments": [...]
}
```

This service will:
1. ✅ Verify the shared secret  
2. 🧠 Use Gemini LLM to generate a minimal frontend app  
3. 📁 Create a public GitHub repository  
4. 🚀 Push code + README.md + LICENSE  
5. 🌐 Enable GitHub Pages  
6. 📤 Report repo_url, commit_sha, and pages_url to the evaluator  

It also supports *Round 2 revisions*, updating the same repo with new features.

***

## 🛠 Features

- **Fully automated** build → deploy → report pipeline  
- **LLM-powered code generation** (Gemini/OpenAI-compatible)  
- **GitHub API integration** for repo creation and file upload  
- **MIT-licensed** and clean Git history (no secrets!)  
- **Idempotent task handling** with nonce validation  
- **Exponential backoff** for evaluation reporting retries  
- **Supports both Round 1 and Round 2** tasks  
- **Professional README.md** and MIT license in every generated repo  
- **Attachment support** for data URIs and files

***

## 📦 Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)  
- **LLM:** Gemini API (Google AI Studio)  
- **GitHub:** REST API v3 for repo & file management  
- **Deployment:** Render.com (public API hosting)  
- **Testing:** Playwright-compatible output

***

## ⚙️ Setup & Configuration

### Prerequisites
- Python 3.8+
- GitHub Personal Access Token (with `repo` and `public_repo` scopes)
- Gemini API key (from Google AI Studio)
- Publicly accessible host (e.g., Render.com)

### Environment Variables

Create a `.env` file:
```
APP_SECRET=your_shared_secret_from_google_form
GH_TOKEN=your_github_personal_access_token
GITHUB_USER=23f2001207
GEMINI_API_KEY=your_gemini_api_key
```
> 🔒 **Never commit .env or tokens to Git!** This repo uses .gitignore to prevent leaks.

### Installation

```bash
git clone https://github.com/23f2001207/llm-code-deploy-agent.git
cd llm-code-deploy-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Locally (for testing)

```bash
uvicorn main:app --reload --port 8000
```
> For production, deploy to a cloud provider with HTTPS.

***

## 🌐 API Usage

### Endpoint
`POST /request`

### Request Body (JSON)
Must include:
- `email`
- `secret`
- `task`
- `round` (1 or 2)
- `nonce`
- `brief`
- `evaluation_url`
- `attachments` (optional)

### Response
- **200 OK** — if secret is valid (processing happens asynchronously)
- **401 Unauthorized** — if secret is invalid
- **400 Bad Request** — if JSON is malformed

> The service *responds immediately* and processes the task in the background.

***

## 📁 Repository Structure

```
llm-code-deploy-agent/
├── main.py                # FastAPI app entrypoint
├── generator.py           # LLM code generation and GitHub integration
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

***

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

> All *generated student apps* also include an MIT license in their root directory, as required by the assignment.

***

## 🧪 Evaluation Compliance

This implementation satisfies all required checks:
- ✅ Public GitHub repo with MIT license  
- ✅ Professional README.md in generated apps  
- ✅ No secrets in Git history  
- ✅ GitHub Pages enabled and functional  
- ✅ Timely reporting to evaluation_url  
- ✅ Supports Round 2 updates  

Generated apps are tested against:
- Static rules (license, README)
- LLM-based code quality
- Playwright dynamic tests (e.g., ?url= handling)

***

## 🙌 Acknowledgements

- Built for the *TDS* course project - 1 : *LLM Code Deployment*
- Inspired by AI-assisted software engineering research  
- Uses GitHub REST API and Gemini completions  
- Special thanks to instructors and the open-source community

***

## ⭐ Support

If you found this project useful or learned something from it, please give it a ⭐ on GitHub — it helps others discover the project too!

***

### ❤ Thank You for Visiting!

Keep coding, keep deploying, and keep learning!  
Made with 💻 and ☕ by **Aryan Naresh Dayalani**

***

## 📬 Contact

For questions about this implementation:  
**Author:** Aryan Naresh Dayalani  
**Roll No:** 23f2001207  
**GitHub:** [@23f2001207](https://github.com/23f2001207)

***

> 🚀 Automating the future of software development—one LLM-generated app at a time.

***
