from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from generator import build_and_deploy, post_evaluation

print("APP_SECRET:", os.getenv("APP_SECRET"))
print("GITHUB_USER:", os.getenv("GITHUB_USER"))
print("GH_TOKEN:", os.getenv("GH_TOKEN"))

app = FastAPI()

SECRET = os.getenv("APP_SECRET", "aryan-secret")
GITHUB_USER = os.getenv("GITHUB_USER", "")
GH_TOKEN = os.getenv("GH_TOKEN", "")

class RequestPayload(BaseModel):
    email: str
    secret: str
    task: str
    nonce: str
    brief: str = ""
    attachments: list = []
    evaluation_url: str
    round: int = 1

@app.post("/request")
async def receive_request(payload: RequestPayload):
    if payload.secret != SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")
    result = build_and_deploy(payload.dict())
    post_evaluation(payload.dict(), result)
    return {"status": "ok", "message": "App built and evaluation ping sent."}
