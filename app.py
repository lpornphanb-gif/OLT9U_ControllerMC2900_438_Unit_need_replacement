import os
import pandas as pd
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
EXCEL_FILE = "Controller_MC2900_438Unit_need replacement.xlsx"
SN_COLUMN = "SN"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def load_sn_set():
    try:
        df = pd.read_excel(EXCEL_FILE, dtype=str)
        df.columns = df.columns.str.strip()
        col = None
        for c in df.columns:
            if c.strip().upper() == SN_COLUMN.upper():
                col = c
                break
        if col is None:
            print(f"[WARN] ไม่พบ column '{SN_COLUMN}' — columns ที่มี: {df.columns.tolist()}")
            return set()
        sn_set = set(df[col].dropna().str.strip().str.upper())
        print(f"[INFO] โหลด SN สำเร็จ: {len(sn_set)} รายการ")
        return sn_set
    except Exception as e:
        print(f"[ERROR] โหลด Excel ไม่ได้: {e}")
        return set()

SN_SET = load_sn_set()

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip().upper()

    if user_text in SN_SET:
        reply = f"⚠️ SN: {event.message.text.strip()}\nStatus: Need Controller Replacement"
    else:
        reply = f"✅ SN: {event.message.text.strip()}\nStatus: ไม่พบในรายการ (ปกติ)"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

@app.route("/", methods=["GET"])
def index():
    return f"LINE SN Checker Bot is running ✅ | SN loaded: {len(SN_SET)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
