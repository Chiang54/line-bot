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

    

    # 如果是傳送位置
    if "message" in data and "location" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        lat = data["message"]["location"]["latitude"]
        lon = data["message"]["location"]["longitude"]
        weather_info = get_weather(lat, lon)
        send_message(chat_id, weather_info)
        send_welcome(chat_id)

    # 如果是純文字訊息
    elif "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_welcome(chat_id)
        elif text == "📡 查天氣":
            send_location_request(chat_id)
        elif text == "📰 看新聞":
            send_message(chat_id, "這裡是今日新聞頭條：\n1. FastAPI 機器人爆紅！")
        elif text =="📡 返回":
            send_welcome(chat_id)
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
            "keyboard": [[{"text": "📡 返回"}, {
                "text": "📍 傳送位置",
                "request_location": True
            }]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    }
    requests.post(url, json=payload)

# 取得天氣
def get_weather(lat, lon):
    url = f"https://wttr.in/{lat},{lon}?format=j1"
    res = requests.get(url).json()
    if "current_condition" in res:
        curr = res["current_condition"][0]
        desc = curr["weatherDesc"][0]["value"]
        temp = curr["temp_C"]
        feels = curr["FeelsLikeC"]
        humidity = curr["humidity"]
        return (
            f"🌤️ 狀態：{desc}\n"
            f"🌡️ 氣溫：{temp}°C（體感 {feels}°C）\n"
            f"💧 濕度：{humidity}%"
        )
    else:
        return "無法取得天氣資料（wttr.in）。"
