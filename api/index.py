from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from chat import get_response
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(data: dict):
    try:
        message = data.get('message')
        if not message or not isinstance(message, str) or not message.strip():
            raise HTTPException(status_code=400, detail="Valid message required")
        response = get_response(message.strip())
        return {"response": response}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health():
    return {"status": "ok"}