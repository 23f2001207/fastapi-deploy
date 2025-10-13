from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Set your secret here or use an environment variable for security
APP_SECRET = os.getenv("APP_SECRET", "aryan-secret")

@app.post("/request")
async def receive_request(request: Request):
    data = await request.json()
    # Secret verification
    if "secret" not in data or data["secret"] != APP_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")
    # Respond with a simple JSON
    return JSONResponse({"status": "ok", "message": "Secret verified!"})
