from flask import Flask, request
import sqlite3
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent, JoinEvent
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "tZrFFIa95iCbOhtqAvCsgnKkKDxkM9j3svTdwFuV4NzOwFmN7apwQlW01n6ypXmBVV7C+O61tyTRfSpr6YOLuOqR+JIQsrJWp7N7oP5MEFe/rD3MVi+41N11FJuCdxmRLmWAwYZFVLqmp1Is2RLUtQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "5bdadf0ba3ab9835420939e9c2fa091b"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

DB_NAME = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line_user_id TEXT,
            game_uid TEXT,
            amount TEXT,
            payment TEXT,
            status TEXT DEFAULT '等待客服確認',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def reply(reply_token, text):
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )

def create_order(line_user_id, game_uid, amount, payment):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (line_user_id, game_uid, amount, payment)
        VALUES (?, ?, ?, ?)
    """, (line_user_id, game_uid, amount, payment))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

@app.route("/")
def home():
    return "金幣多官方LINE客服系統運作中"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature"

    return "OK"

@handler.add(FollowEvent)
def handle_follow(event):
    reply(event.reply_token,
        "🎰 歡迎加入【金幣多】官方客服\n\n"
        "請輸入：\n"
        "【買幣】我要購買遊戲幣\n"
        "【幣值】查詢目前參考幣值\n"
        "【付款】查看付款方式\n"
        "【客服】聯繫專人\n\n"
        "⚠️ 所有交易需由客服人工確認後處理。"
    )

@handler.add(JoinEvent)
def handle_join(event):
    reply(event.reply_token,
        "🎉 金幣多客服已加入群組\n\n"
        "請輸入【買幣】開始登記需求。"
    )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()
    user_id = getattr(event.source, "user_id", "unknown")

    if msg in ["你好", "哈囉", "hi", "Hi", "HI"]:
        reply(event.reply_token,
            "您好，歡迎使用金幣多官方客服 👋\n\n"
            "請輸入：\n"
            "【買幣】我要購買遊戲幣\n"
            "【幣值】查詢幣值\n"
            "【付款】付款方式\n"
            "【客服】聯繫專人"
        )

    elif "買幣" in msg or "我要買" in msg:
        reply(event.reply_token,
            "📝 買幣需求登記\n\n"
            "請照格式輸入：\n"
            "下單 UID 金額 付款方式\n\n"
            "範例：\n"
            "下單 123456789 3000 轉帳\n\n"
            "付款方式可填：轉帳、LINE Pay、街口、超商代碼"
        )

    elif msg.startswith("下單"):
        parts = msg.split()

        if len(parts) < 4:
            reply(event.reply_token,
                "格式錯誤，請照這樣輸入：\n\n"
                "下單 UID 金額 付款方式\n\n"
                "範例：\n"
                "下單 123456789 3000 轉帳"
            )
        else:
            game_uid = parts[1]
            amount = parts[2]
            payment = parts[3]

            order_id = create_order(user_id, game_uid, amount, payment)

            reply(event.reply_token,
                f"✅ 需求已送出\n\n"
                f"訂單編號：#{order_id}\n"
                f"遊戲UID：{game_uid}\n"
                f"金額：{amount}\n"
                f"付款方式：{payment}\n"
                f"狀態：等待客服確認\n\n"
                "客服確認後會再與您聯繫。\n"
                "⚠️ 請勿自行轉帳，請依客服當下安排為主。"
            )

    elif "幣值" in msg or "價格" in msg:
        reply(event.reply_token,
            "💰 目前參考幣值\n\n"
            "買幣：130\n"
            "賣幣：144\n\n"
            "⚠️ 實際幣值依客服當下報價為主。"
        )

    elif "付款" in msg or "支付" in msg:
        reply(event.reply_token,
            "💳 支付方式\n\n"
            "✅ 轉帳\n"
            "✅ LINE Pay\n"
            "✅ 街口支付\n"
            "✅ iPASS MONEY\n"
            "✅ 超商代碼\n\n"
            "⚠️ 實際付款帳號請以客服當下提供為主。"
        )

    elif "客服" in msg or "找人" in msg:
        reply(event.reply_token,
            "📞 金幣多客服\n\n"
            "Line：shop94168\n"
            "服務時間：24H在線\n\n"
            "請等待專人協助。"
        )

    else:
        reply(event.reply_token,
            "您好，我是金幣多客服小幫手 🤖\n\n"
            "請輸入：\n"
            "【買幣】\n"
            "【幣值】\n"
            "【付款】\n"
            "【客服】"
        )

if __name__ == "__main__":
    app.run()
