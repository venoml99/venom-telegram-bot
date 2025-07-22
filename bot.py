from pyrogram import Client, filters
from pyrogram.types import Message
import os
import sqlite3
import random

API_ID = 27717774
API_HASH = "74612099f9ece419b3ed06c02e4082c5"
BOT_TOKEN = "7789076703:AAGY1VhMTsaryJcA2mLXx3MyPnB3Ch2oM80"
FORCE_CHANNEL = "M_H_O_D7"
OWNER_ID = 5401358805
DEVELOPER_USERNAME = "@VENOM_L99"

app = Client("venom-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاعدة بيانات النقاط
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, banned INTEGER DEFAULT 0)")
conn.commit()

# اشتراك إجباري
async def is_subscribed(user_id):
    try:
        member = await app.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

# حفظ المستخدم
def save_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

# التحقق من الحظر
def is_banned(user_id):
    cursor.execute("SELECT banned FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] == 1

# زيادة النقاط
def add_point(user_id):
    cursor.execute("UPDATE users SET points = points + 1 WHERE id = ?", (user_id,))
    conn.commit()

# نقاط المستخدم
def get_points(user_id):
    cursor.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

# المتصدرين
def get_leaderboard():
    cursor.execute("SELECT id, points FROM users ORDER BY points DESC LIMIT 10")
    return cursor.fetchall()

# رسالة البداية
@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id

    if not await is_subscribed(user_id):
        await message.reply(f"🚫 اشترك أولًا في القناة لاستخدام البوت:\n\n👉 https://t.me/{FORCE_CHANNEL}")
        return

    if is_banned(user_id):
        await message.reply("🚷 لقد تم حظرك من استخدام هذا البوت.")
        return

    save_user(user_id)
    await message.reply(f"👋 أهلًا بك {message.from_user.first_name}!\n🎮 أرسل /help لعرض الأوامر.\n\n👤 المطور: {DEVELOPER_USERNAME}")

# الأوامر
@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await message.reply(
        "🎮 أوامر المستخدم:\n"
        "/xo - لعبة XO\n"
        "/dice - نرد عشوائي\n"
        "/quiz - سؤال ثقافي\n"
        "/points - نقاطك\n\n"
        "👮 أوامر المطور:\n"
        "/ban [id]\n"
        "/unban [id]\n"
        "/reset\n"
        "/leaderboard"
    )

@app.on_message(filters.command("dice"))
async def dice(client, message: Message):
    if is_banned(message.from_user.id): return
    await message.reply_dice()
    add_point(message.from_user.id)

@app.on_message(filters.command("xo"))
async def xo(client, message: Message):
    if is_banned(message.from_user.id): return
    await message.reply("❌⭕ أرسل 'X' أو 'O' للعب مع نفسك 🤪")
    add_point(message.from_user.id)

@app.on_message(filters.command("quiz"))
async def quiz(client, message: Message):
    if is_banned(message.from_user.id): return
    questions = [
        ("ما هي عاصمة اليابان؟", "طوكيو"),
        ("كم عدد قارات العالم؟", "7"),
        ("ما هو الكوكب الأحمر؟", "المريخ"),
    ]
    q = random.choice(questions)
    await message.reply(f"❓ سؤال:\n{q[0]}\n\n💬 أجب برسالة جديدة.")
    app.set_parse_mode("html")
    app.quiz_answer = q[1]
    add_point(message.from_user.id)

@app.on_message(filters.command("points"))
async def points(client, message: Message):
    points = get_points(message.from_user.id)
    await message.reply(f"🏅 نقاطك: {points}")

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban(client, message: Message):
    try:
        uid = int(message.command[1])
        cursor.execute("UPDATE users SET banned = 1 WHERE id = ?", (uid,))
        conn.commit()
        await message.reply("🚫 تم الحظر.")
    except:
        await message.reply("❌ استخدم: /ban [id]")

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban(client, message: Message):
    try:
        uid = int(message.command[1])
        cursor.execute("UPDATE users SET banned = 0 WHERE id = ?", (uid,))
        conn.commit()
        await message.reply("✅ تم إلغاء الحظر.")
    except:
        await message.reply("❌ استخدم: /unban [id]")

@app.on_message(filters.command("reset") & filters.user(OWNER_ID))
async def reset_points(client, message: Message):
    cursor.execute("UPDATE users SET points = 0")
    conn.commit()
    await message.reply("🔄 تم تصفير جميع النقاط.")

@app.on_message(filters.command("leaderboard"))
async def leaderboard(client, message: Message):
    top = get_leaderboard()
    text = "🏆 المتصدرين:\n"
    for i, (uid, pts) in enumerate(top, start=1):
        text += f"{i}. <code>{uid}</code> - {pts} نقطة\n"
    await message.reply(text)

app.run()
