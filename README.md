# LINE SN Checker Bot 🤖

Bot รับ SN จาก LINE แล้วเช็คในไฟล์ Excel — ถ้าพบ ตอบ "Need Controller Replacement"

---

## 📋 ขั้นตอนทั้งหมด (ทำครั้งเดียว ~30 นาที)

### STEP 1 — สร้าง LINE Official Account (ฟรี)
1. ไปที่ https://manager.line.biz → สมัครฟรี
2. หลังสร้าง OA → ไปที่ **Settings → Messaging API → Enable Messaging API**
3. กด **Issue** เพื่อรับ **Channel Secret** และ **Channel Access Token**
4. จดไว้ทั้งสอง (จะใช้ใน Step 3)

### STEP 2 — อัปโหลดโปรเจกต์ขึ้น Railway (ฟรี)
1. สมัคร https://railway.app ด้วย GitHub account
2. กด **New Project → Deploy from GitHub**
3. อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์นี้ขึ้น GitHub repo ก่อน
   - รวมไฟล์ **438_Unit.xlsx** ด้วย (วางในโฟลเดอร์เดียวกับ app.py)
4. Railway จะ deploy อัตโนมัติ → รอจนได้ URL เช่น `https://xxx.railway.app`

### STEP 3 — ตั้งค่า Environment Variables บน Railway
ไปที่ Variables tab ใน Railway แล้วเพิ่ม:
```
LINE_CHANNEL_ACCESS_TOKEN = (ค่าจาก Step 1)
LINE_CHANNEL_SECRET       = (ค่าจาก Step 1)
```

### STEP 4 — ตั้ง Webhook URL ใน LINE
1. กลับไปที่ LINE Developers Console
2. ใส่ Webhook URL: `https://xxx.railway.app/webhook`
3. กด **Verify** → ต้องขึ้น Success
4. เปิด **Use webhook = ON**

### STEP 5 — แก้ชื่อ Column (สำคัญ!)
เปิดไฟล์ `app.py` บรรทัด:
```python
SN_COLUMN = "SN"   # ← แก้เป็นชื่อ column จริงในไฟล์ Excel
```
ตรวจสอบชื่อ column ในไฟล์ Excel ก่อน (เช่น "Serial No", "S/N", "SN")

---

## 💬 วิธีใช้งาน
- เพิ่มบัญชี LINE OA เป็นเพื่อน
- พิม SN ส่งเข้ามา เช่น `SN001234`
- Bot จะตอบกลับทันที:
  - ❌ พบในรายการ → `⚠️ Need Controller Replacement`
  - ✅ ไม่พบ → `ปกติ`

---

## 📁 โครงสร้างไฟล์
```
line-bot/
├── app.py              ← โค้ด bot หลัก
├── 438_Unit.xlsx       ← ไฟล์ข้อมูล SN (วางตรงนี้)
├── requirements.txt    ← Python packages
├── Procfile            ← สำหรับ Railway/Heroku
├── runtime.txt         ← Python version
└── README.md           ← ไฟล์นี้
```
