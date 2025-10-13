from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Replace 'your-chosen-secret' below with the actual secret text you want
SECRET = "aryan-secret"

class SecretRequest(BaseModel):
    secret: str

@app.post("/request")
async def receive_request(data: SecretRequest):
    if data.secret != SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")
    return {"status": "ok", "message": "Secret verified!"}
