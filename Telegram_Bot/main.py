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

        if text == "/start":
            send_welcome(chat_id)
        elif text == "📡 查天氣":
            send_message(chat_id, "目前天氣晴朗 ☀️（假資料）")
        elif text == "📰 看新聞":
            send_message(chat_id, "這裡是今日新聞頭條：\n1. FastAPI 機器人爆紅！")
        else:
            send_message(chat_id, f"你說的是：{text}")
    
    elif "inline_query" in data:
        inline_query_id = data["inline_query"]["id"]
        query = data["inline_query"]["query"]
        results = [{
            "type": "article",
            "id": "1",
            "title": f"搜尋結果：{query}",
            "input_message_content": {
                "message_text": f"你輸入的是：{query}"
            }
        }]
        answer_inline_query(inline_query_id, results)
    return {"status": "ok"}


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# 開始按鈕設定
def send_welcome(chat_id):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "👋 歡迎使用 *村榮商店* 機器人！請選擇功能 👇",
        "reply_markup": {
            "keyboard": [
                [{"text": "📡 查天氣"}, {"text": "📰 看新聞"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    }
    requests.post(url, json=payload)

# inLine設定
def answer_inline_query(inline_query_id, results):
    url = f"{TELEGRAM_API}/answerInlineQuery"
    payload = {
        "inline_query_id": inline_query_id,
        "results": results,
        "cache_time": 1
    }
    requests.post(url, json=payload)

# 取得使用者位置
def send_location_request(chat_id):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "請傳送你的位置，我會回覆你當地的天氣 ☁️",
        "reply_markup": {
            "keyboard": [[{
                "text": "📍 傳送位置",
                "request_location": True
            }]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    }
    requests.post(url, json=payload)