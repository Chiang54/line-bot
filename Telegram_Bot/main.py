from fastapi import APIRouter, Request
import os
import requests
import feedparser
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# 初始化
router = APIRouter()
load_dotenv()
logging.basicConfig(level=logging.INFO)

# 常數定義
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
NEWS_FEED_URL = "https://news.google.com/news/rss/headlines?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"


@router.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
        logging.info(f"Webhook 收到資料：{data}")

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]

            if "location" in message:
                lat = message["location"]["latitude"]
                lon = message["location"]["longitude"]
                weather_info = get_weather(lat, lon)
                send_message(chat_id, weather_info)
                send_main_menu(chat_id)

            elif "text" in message:
                text = message["text"]
                handle_text_message(chat_id, text)

        elif "callback_query" in data:
            handle_callback(data["callback_query"])

    except Exception as e:
        logging.error(f"處理 webhook 時發生錯誤：{e}")
    
    return {"status": "ok"}

# 處理純文字訊息
def handle_text_message(chat_id: int, text: str):
    if text == "/start":
        send_main_menu(chat_id)
    elif text == "📍 傳送位置":
        send_location_request(chat_id)
    else:
        send_message(chat_id, f"你說的是：{text}")

# 處理 Callback 回傳
def handle_callback(callback_data: Dict[str, Any]):
    chat_id = callback_data["message"]["chat"]["id"]
    data_id = callback_data["data"]

    if data_id == "weather":
        send_location_request(chat_id)
    elif data_id == "news":
        send_news_headlines(chat_id)
    elif data_id == "back":
        send_main_menu(chat_id)

# 主選單
def send_main_menu(chat_id: int):
    text = "👋 歡迎使用 *村榮商店* 機器人！請選擇功能 👇"
    keyboard = [
        [{"text": "📡 查天氣", "callback_data": "weather"}],
        [{"text": "📰 看新聞", "callback_data": "news"}]
    ]
    send_message(chat_id, text, keyboard)

# 請用戶傳送位置
def send_location_request(chat_id: int):
    text = "📍 請傳送你的位置，我會回覆你當地的天氣 ☁️"
    keyboard = [
        [{"text": "🔙 返回", "callback_data": "back"}],
        [{"text": "📍 傳送位置", "request_location": True}]
    ]
    send_message(chat_id, text, keyboard)

# 查天氣
def get_weather(lat: float, lon: float) -> str:
    try:
        url = f"https://wttr.in/{lat},{lon}?format=j1"
        res = requests.get(url, timeout=5).json()
        curr = res.get("current_condition", [{}])[0]

        desc = curr.get("weatherDesc", [{}])[0].get("value", "未知")
        temp = curr.get("temp_C", "?")
        feels = curr.get("FeelsLikeC", "?")
        humidity = curr.get("humidity", "?")

        return (
            f"🌤️ 狀態：{desc}\n"
            f"🌡️ 氣溫：{temp}°C（體感 {feels}°C）\n"
            f"💧 濕度：{humidity}%"
        )
    except Exception as e:
        logging.error(f"查天氣時出錯：{e}")
        return f"❌ 查詢錯誤：{str(e)}"

# 取得新聞
def send_news_headlines(chat_id: int):
    try:
        feed = feedparser.parse(NEWS_FEED_URL)
        headlines = "\n".join(
            f"🔹 [{entry.title}]({entry.link})" for entry in feed.entries[:5]
        )
        send_message(chat_id, f"📰 今日新聞頭條：\n\n{headlines}")
    except Exception as e:
        logging.error(f"讀取新聞失敗：{e}")
        send_message(chat_id, "⚠️ 無法取得新聞，請稍後再試。")

# 發送訊息 (可選按鈕)
def send_message(chat_id: int, text: str, keyboard: list = None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"傳送訊息失敗：{e}")
