from fastapi import APIRouter, Request
import os
import requests
from dotenv import load_dotenv
import logging

router = APIRouter()
load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


@router.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    logging.info(f"Webhook 收到資料：{data}")

    # 使用者傳送位置
    if "message" in data and "location" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        lat = data["message"]["location"]["latitude"]
        lon = data["message"]["location"]["longitude"]
        weather_info = get_weather(lat, lon)
        send_message(chat_id, weather_info)
        send_main_menu(chat_id)

    # 純文字訊息處理
    elif "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_main_menu(chat_id)
        elif text == "📍 傳送位置":
            send_location_request(chat_id)
        else:
            send_message(chat_id, f"你說的是：{text}")

    # Callback 按鈕點擊
    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_id = query["data"]

        if data_id == "weather":
            send_location_request(chat_id)
        elif data_id == "news":
            send_message(chat_id, "📰 這裡是今日新聞頭條：\n1. FastAPI 機器人爆紅！")
        elif data_id == "back":
            send_main_menu(chat_id)

    return {"status": "ok"}


# 主選單
def send_main_menu(chat_id):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "👋 歡迎使用 *村榮商店* 機器人！請選擇功能 👇",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "📡 查天氣", "callback_data": "weather"}],
                [{"text": "📰 看新聞", "callback_data": "news"}]
            ]
        }
    }
    requests.post(url, json=payload)

# 查天氣的「請傳位置」
def send_location_request(chat_id):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "📍 請傳送你的位置，我會回覆你當地的天氣 ☁️",
        "reply_markup": {
            "keyboard": [[{"text": "📍 傳送位置", "request_location": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    }
    requests.post(url, json=payload)

# 查天氣邏輯
def get_weather(lat, lon):
    try:
        url = f"https://wttr.in/{lat},{lon}?format=j1"
        res = requests.get(url, timeout=5).json()
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
            return "⚠️ 無法取得天氣資料，請稍後再試。"
    except Exception as e:
        return f"❌ 查詢錯誤：{str(e)}"

# 發送一般訊息
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)
