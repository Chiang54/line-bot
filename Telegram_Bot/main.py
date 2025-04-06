# app/routers/crawler.py
from fastapi import APIRouter, FastAPI, Request
import os
import requests
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


@router.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = f"你說的是：{text}"
        send_message(chat_id, reply)
    return {"status": "ok"}


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)