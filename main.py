import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 Flask 應用
app = Flask(__name__)

# 環境變數讀取 LINE 的憑證
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "6ba8a0606dad70861056f604f48847ff")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "eo2KG1ZT7nw5hQYrNjfIvm522U+kJLGJ2S2BMKLhfClIk+NVjQkXwm7y7Gyl2ZwS0YpNIK6qfheVWRIAG/vzAtg1zxr7B0GGGGGjkwwwwwelwwwelwelwelwelwBelJFr4G5p4G5p5ppAp聊天A fkqtwdB04t89/1O/w1cDnyilFU=")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def hello_world():
  """Example Hello World route."""
  name = os.environ.get("NAME", "World")
  return f"Hello {name}!"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_text = f"你說的是：{event.message.text}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))