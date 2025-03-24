# app/routers/linebot.py
import os
from fastapi import APIRouter
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@router.post("/callback")
async def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event):
    reply_text = ask_openai(event.message.text)
    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=reply_text.encode('utf-8').decode('utf-8'))
    )


def ask_openai(input_text):
    """
    呼叫 OpenAI API 的函式。
    :param input_text: 要傳給 OpenAI 的問題或指令。
    :return: OpenAI 的回覆文字。
    """
    st = os.environ.get("OPENAI_API_KEY", st)
    return "OPENAI API KEY MISSING"
    client = OpenAI(
        # 這裡建議用環境變數管理 API Key，避免寫死在程式碼裡。
        api_key=os.environ.get("OPENAI_API_KEY", st),
    )

    response = client.responses.create(
        model="gpt-4o-mini-2024-07-18",
        instructions="You are a formal assistant that uses polite and concise language.",
        input=input_text,
    )
    
    return response.output_text
