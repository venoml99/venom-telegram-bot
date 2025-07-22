import json
import telebot
from telebot import types

# --------------- إعدادات البوت ---------------
TOKEN = "7789076703:AAGY1VhMTsaryJcA2mLXx3MyPnB3Ch2oM80"
DEVELOPER_ID = 5401358805
CHANNEL_USERNAME = "M_H_O_D7"
DEVELOPER_USERNAME = "VENOM_L99"

DATA_FILE = "bot_data.json"

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        points = data.get("points", {})
        banned_users = set(data.get("banned", []))
        user_data = data.get("users", {})
except FileNotFoundError:
    points = {}
    banned_users = set()
    user_data = {}

notified_users_1000 = set()
bot = telebot.TeleBot(TOKEN, threaded=False)

try:
    BOT_ID = bot.get_me().id
except:
    BOT_ID = None

# --------------- دوال مساعدة ---------------
def save_data():
    data = {
        "points": points,
        "banned": list(banned_users),
        "users": user_data
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def is_subscribed(user_id):
    try:
        bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return True
    except:
        return False

def add_points(chat_id, user_id, amount):
    chat_id = str(chat_id)
    user_id = str(user_id)
    if chat_id not in points:
        points[chat_id] = {}
    if user_id not in points[chat_id]:
        points[chat_id][user_id] = 0
    points[chat_id][user_id] += amount
    save_data()
    return points[chat_id][user_id]

# --------------- أوامر البوت ---------------
@bot.message_handler(commands=["start"])
def start_handler(message):
    if message.chat.type == "private":
        bot.send_message(message.chat.id,
            f"مرحباً بك في بوت الألعاب 🎮\n"
            f"يجب الاشتراك في قناة @{CHANNEL_USERNAME} لاستخدام البوت.\n"
            f"استخدم /games لعرض قائمة الألعاب.")

@bot.message_handler(commands=["games"])
def games_handler(message):
    bot.reply_to(message,
        "🕹️ قائمة الألعاب:\n"
        "/xo - لعبة XO\n"
        "/dice - لعبة النرد\n"
        "/riddle - لغز عشوائي\n"
        "/quiz - سؤال ثقافي\n"
        "/leaderboard - المتصدرين\n\n"
        "يجب الاشتراك في القناة: @" + CHANNEL_USERNAME)

@bot.message_handler(commands=["dice"])
def dice_handler(message):
    user = message.from_user
    if not is_subscribed(user.id):
        bot.reply_to(message, f"❌ اشترك أولاً في @{CHANNEL_USERNAME}")
        return
    dice_msg = bot.send_dice(message.chat.id)
    value = dice_msg.dice.value
    gained = 0
    if value == 6:
        gained = 10
    elif value == 5:
        gained = 5
    if gained > 0:
        score = add_points(message.chat.id, user.id, gained)
        bot.send_message(message.chat.id, f"🎉 ربحت {gained} نقطة! مجموعك الآن: {score}")
    else:
        bot.send_message(message.chat.id, "❗ لم تربح نقاط هذه المرة، جرب مجددًا!")

# يمكنك إضافة بقية الأوامر مثل /xo و /quiz و /riddle بنفس النمط

bot.infinity_polling()
