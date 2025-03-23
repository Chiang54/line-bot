import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

# 初始化 Flask 應用
app = Flask(__name__)

# 環境變數讀取 LINE 的憑證
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "6ba8a0606dad70861056f604f48847ff")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "eo2KG1ZT7nw5hQYrNjfIvm522U+kJLGJ2S2BMKLhfClIk+NVjQkXwm7y7Gyl2ZwS0YpNIK6qfheVWRIAG/vzAtg1zxr7B0GkTGSB4cjh+X5CKig/RqlPojWp4VRACPt7WjlFXIYL2qBSFPaL6fkqtwdB04t89/1O/w1cDnyilFU=")

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
    st = "sk-proj-f8FiK-spUjv_3uB"
    st += "XLNUzW1N1MQQUAevUERkg9HB"
    st += "TOrxE_kbIBnyRJC5LAWGGhFkts"
    st += "vj2qE9KRKT3BlbkFJvcrsGpps4P"
    st += "PUUNBrl64ax81huKCEXXxcZVDDh"
    st += "BsGUIiq3LHfUaWn3Cy"
    st += "GsmicPPyGxsTfmc7EUA"
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


if __name__ == "__main__":

    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
