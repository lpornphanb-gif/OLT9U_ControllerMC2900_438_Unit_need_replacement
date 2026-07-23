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

EXCEL_SN   = "OLT9U_ControllerMC2900_438_Unit_need_replacement.xlsx"
EXCEL_SITE = "SITE_OLT_INFO.xlsx"
SN_COLUMN  = "check SN"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def load_sn_set():
    try:
        df = pd.read_excel(EXCEL_SN, dtype=str)
        df.columns = df.columns.str.strip()
        col = next((c for c in df.columns if c.strip().upper() == SN_COLUMN.upper()), None)
        if col is None:
            print(f"[WARN] ไม่พบ column '{SN_COLUMN}'")
            return set()
        sn_set = set(df[col].dropna().str.strip().str.upper())
        print(f"[INFO] โหลด SN: {len(sn_set)} รายการ")
        return sn_set
    except Exception as e:
        print(f"[ERROR] โหลด SN ไม่ได้: {e}")
        return set()

def load_site_df():
    try:
        df = pd.read_excel(EXCEL_SITE, dtype=str, header=1)
        df.columns = df.columns.str.strip()
        print(f"[INFO] โหลด Site: {len(df)} รายการ")
        return df
    except Exception as e:
        print(f"[ERROR] โหลด Site ไม่ได้: {e}")
        return pd.DataFrame()

SN_SET  = load_sn_set()
SITE_DF = load_site_df()

HELP_MSG = (
    "🤖 คำสั่งที่ใช้ได้\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "1️⃣ ตรวจสอบ Controller\n"
    "-check [SN]\n"
    "ตัวอย่าง: -check Z530071250200278\n\n"
    "2️⃣ ดูข้อมูล Site\n"
    "-siteinfo [ชื่อ Site หรือ OLT]\n"
    "ตัวอย่าง: -siteinfo CRI0145\n"
    "ตัวอย่าง: -siteinfo OLT-BKK-01\n\n"
    "3️⃣ ดูคำสั่งทั้งหมด\n"
    "-help\n"
    "━━━━━━━━━━━━━━━━━━━━━━"
)

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
    user_text = event.message.text.strip()
    reply = None

    # ----- -help -----
    if user_text.lower() == "-help":
        reply = HELP_MSG

    # ----- -check -----
    elif user_text.lower().startswith("-check "):
        sn = user_text[7:].strip().upper()
        if sn in SN_SET:
            reply = f"⚠️ SN: {sn}\nStatus: Need Controller Replacement"
        else:
            reply = f"✅ SN: {sn}\nStatus: No Need Replacement\n\nรบกวนพี่ๆทดสอบการใช้งานหน้างานของ Controller ด้วยนะคะ"

    # ----- -siteinfo -----
    elif user_text.lower().startswith("-siteinfo "):
        keyword = user_text[10:].strip().upper()
        if SITE_DF.empty:
            reply = "❌ โหลดข้อมูล Site ไม่ได้ครับ"
        else:
            # ค้นหาจาก Site Name หรือ OLT Name
            mask = (
                SITE_DF["Site Name"].str.strip().str.upper() == keyword
            ) | (
                SITE_DF["OLT Name"].str.strip().str.upper() == keyword
            )
            results = SITE_DF[mask]
            if results.empty:
                reply = f"❌ ไม่พบข้อมูล: {user_text[10:].strip()}\n\nลองพิม -help เพื่อดูวิธีใช้"
            else:
                row = results.iloc[0]
                lat = row.get("Lat (Original)", "")
                lon = row.get("Lon (Original)", "")
                maps_url = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "ไม่มีข้อมูล"
                reply = (
                    f"📍 Site Info\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏢 Site Name : {row.get('Site Name', '')}\n"
                    f"📡 OLT Name  : {row.get('OLT Name', '')}\n"
                    f"🏷️ Site ID   : {row.get('Site ID', '')}\n"
                    f"🏭 Vendor    : {row.get('Vendor', '')}\n"
                    f"📍 Lat       : {lat}\n"
                    f"📍 Lon       : {lon}\n"
                    f"🌐 IP        : {row.get('IP Rectifier', '')}\n"
                    f"🔀 Gateway   : {row.get('IP Gateway', '')}\n"
                    f"🔌 Port      : {row.get('Port', '')}\n"
                    f"🔢 Subnet    : {row.get('Subnet Mask', '')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🗺️ Google Maps:\n{maps_url}"
                )

    if reply:
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
    return f"LINE Bot ✅ | SN: {len(SN_SET)} | Site: {len(SITE_DF)} รายการ"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
