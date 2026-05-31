from flask import Flask, request

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "tZrFFIa95iCbOhtqAvCsgnKkKDxkM9j3svTdwFuV4NzOwFmN7apwQlW01n6ypXmBVV7C+O61tyTRfSpr6YOLuOqR+JIQsrJWp7N7oP5MEFe/rD3MVi+41N11FJuCdxmRLmWAwYZFVLqmp1Is2RLUtQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "5bdadf0ba3ab9835420939e9c2fa091b"

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def home():
    return "LINE BOT OK"

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature'

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_message = event.message.text

    if "幣值" in user_message:
        reply_text = "💰目前參考幣值：130 / 144"

    elif "客服" in user_message:
        reply_text = "📞客服Line：shop94168"

    elif "公會" in user_message:
        reply_text = (
            "🤝合作公會\n\n"
            "⚔️ 黃金甲\n"
            "👁️ 黃金瞳\n"
            "🏠 黃金屋\n"
            "🛡️ 黃金矛\n"
            "👟 黃金靴"
        )

    else:
        reply_text = (
            "🎰金幣多小幫手🎰\n\n"
            "請輸入：\n"
            "【幣值】\n"
            "【客服】\n"
            "【公會】"
        )

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=reply_text)
                ]
            )
        )

if __name__ == "__main__":
    app.run()
