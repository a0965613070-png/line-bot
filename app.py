from flask import Flask, request
import sqlite3

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent, JoinEvent, MemberJoinedEvent
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "你的CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET = "你的CHANNEL_SECRET"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

DB_NAME = "players.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            line_user_id TEXT PRIMARY KEY,
            game_uid TEXT,
            nickname TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def reply(reply_token, text):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )


def bind_uid(line_user_id, game_uid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO players (line_user_id, game_uid)
        VALUES (?, ?)
        ON CONFLICT(line_user_id)
        DO UPDATE SET game_uid = excluded.game_uid
    """, (line_user_id, game_uid))
    conn.commit()
    conn.close()


def get_player(line_user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT game_uid, created_at FROM players WHERE line_user_id = ?", (line_user_id,))
    row = c.fetchone()
    conn.close()
    return row


@app.route("/")
def home():
    return "AI客服 BOT 運行中"


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
        "我是 AI 客服小幫手 🤖\n\n"
        "請輸入：\n"
        "【幣值】查詢目前幣值\n"
        "【客服】聯繫專人\n"
        "【公會】查看合作公會\n"
        "【綁定 UID 你的遊戲ID】綁定玩家資料\n"
        "【我的資料】查詢綁定資料"
    )


@handler.add(JoinEvent)
def handle_join(event):
    reply(event.reply_token,
        "🎉 金幣多 AI 客服已加入群組\n\n"
        "可輸入：幣值、客服、公會、綁定 UID、我的資料"
    )


@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    reply(event.reply_token,
        "🎉 歡迎新朋友加入\n\n"
        "需要服務請輸入：\n"
        "【幣值】\n"
        "【客服】\n"
        "【公會】"
    )


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    if msg.startswith("綁定"):
        game_uid = msg.replace("綁定", "").replace("UID", "").replace("uid", "").strip()

        if not game_uid:
            reply(event.reply_token, "請這樣輸入：\n綁定 UID 123456789")
        else:
            bind_uid(user_id, game_uid)
            reply(event.reply_token,
                f"✅ UID綁定成功\n\n"
                f"您的遊戲UID：{game_uid}\n\n"
                "之後可輸入【我的資料】查詢。"
            )

    elif msg == "我的資料":
        player = get_player(user_id)

        if player:
            reply(event.reply_token,
                "📌 您的玩家資料\n\n"
                f"遊戲UID：{player[0]}\n"
                f"綁定時間：{player[1]}"
            )
        else:
            reply(event.reply_token,
                "目前尚未綁定UID。\n\n"
                "請輸入：\n綁定 UID 你的遊戲ID"
            )

    elif "幣值" in msg or "價格" in msg or "匯率" in msg:
        reply(event.reply_token,
            "💰 金幣多｜目前參考幣值\n\n"
            "買幣：130\n"
            "賣幣：144\n\n"
            "⚠️ 實際幣值依當下客服報價為主。"
        )

    elif "客服" in msg or "找人" in msg or "聯繫" in msg:
        reply(event.reply_token,
            "📞 金幣多客服\n\n"
            "Line：shop94168\n"
            "服務時間：24H在線\n\n"
            "✅ 專人協助\n"
            "✅ 處理快速"
        )

    elif "公會" in msg or "合作" in msg:
        reply(event.reply_token,
            "🤝 合作公會列表\n\n"
            "⚔️ 黃金甲\n"
            "👁️ 黃金瞳\n"
            "🏠 黃金屋\n"
            "🛡️ 黃金矛\n"
            "👟 黃金靴"
        )

    elif "你好" in msg or "哈囉" in msg or "hi" in msg.lower():
        reply(event.reply_token,
            "您好 👋\n"
            "我是金幣多 AI 客服小幫手 🤖\n\n"
            "請輸入：\n"
            "【幣值】查詢幣值\n"
            "【客服】聯繫專人\n"
            "【公會】查看公會\n"
            "【綁定 UID 你的遊戲ID】綁定資料\n"
            "【我的資料】查詢資料"
        )

    else:
        reply(event.reply_token,
            "🤖 AI客服小幫手為您服務\n\n"
            "我可以協助：\n"
            "1️⃣ 查詢幣值\n"
            "2️⃣ 聯繫客服\n"
            "3️⃣ 查看合作公會\n"
            "4️⃣ 綁定玩家UID\n"
            "5️⃣ 查詢我的資料\n\n"
            "請輸入關鍵字：幣值、客服、公會、綁定UID、我的資料"
        )


if __name__ == "__main__":
    app.run()
