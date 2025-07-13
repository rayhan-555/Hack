import os
import telebot
import random
import json
import threading
import time
from datetime import datetime
bot.remove_webhook()  # এটা ওয়েবহুক ডিলিট করবে
bot.infinity_polling()  # এটা বটকে পোলিংবে

#pollN ENV or direct paste
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8089047477:AAF4DNls88mau_ayvi6j5WFGHbaJFLEhWqo"
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Channel List File
CHANNEL_FILE = "channels.json"

# 🔄 Load channels
def load_channels():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, 'r') as f:
            return json.load(f)
    return []

# 💾 Save channels
def save_channels(channels):
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(channels, f)

# 🧠 Prediction message
def generate_prediction():
    period_id = datetime.utcnow().strftime("𝟸𝟶%y%m%d") + "𝟷𝟶𝟶𝟶" + str(random.randint(1000, 9999))
    result_text = f"""
<b>💢 𝗛𝗚𝗭𝗬 𝗔𝗨𝗧𝗢 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡 💢</b>

<b>⏳ 𝙿𝙴𝚁𝙸𝙾𝙳 𝙸𝙳 : {period_id}</b>

<b>🚨 𝚁𝙴𝚂𝚄𝙻𝚃 --> {random.choice(['𝐁𝐈𝐆', '𝐒𝐌𝐀𝐋𝐋'])} + {random.choice(['🟢', '🔴'])} + {random.choice(['𝟶','𝟷','𝟸','𝟹','𝟺','𝟻','𝟼','𝟽','𝟾','𝟿'])}</b>

<b>⭕ ᗰᑌՏT ᗷᗴ 7-8 ՏTᗴᑭ ᗰᗩIᑎTᗩIᑎ.</b>
"""
    return result_text

# 🔁 Prediction sender
is_signal_on = False
def prediction_loop():
    while is_signal_on:
        msg = generate_prediction()
        channels = load_channels()
        for ch in channels:
            try:
                bot.send_message(ch, msg, parse_mode='HTML')
            except Exception as e:
                print(f"❌ Error sending to {ch}: {e}")
        time.sleep(60)

# ✅ /start
@bot.message_handler(commands=['start'])
def start(message):
    text = "<b>💢 HGZY Prediction Bot 💢</b>\n\nWelcome! নিচের বাটনগুলো দিয়ে সিগন্যাল নিয়ন্ত্রণ করো।"
    bot.reply_to(message, text, parse_mode='HTML')

# ✅ /addchannel @username
@bot.message_handler(commands=['addchannel'])
def add_channel(message):
    try:
        channel_username = message.text.split(" ", 1)[1]
        if not channel_username.startswith("@"):
            return bot.reply_to(message, "❌ Channel must start with '@'")
        channels = load_channels()
        if channel_username not in channels:
            channels.append(channel_username)
            save_channels(channels)
            bot.reply_to(message, f"✅ Channel {channel_username} added!")
        else:
            bot.reply_to(message, "⚠️ Already added.")
    except:
        bot.reply_to(message, "Usage: /addchannel @channel")

# ✅ /channellist
@bot.message_handler(commands=['channellist'])
def ch_list(message):
    channels = load_channels()
    if channels:
        msg = "<b>🔴 All Channel Link ⤵️</b>\n\n"
        for ch in channels:
            msg += f"<b>Channel -----> {ch}\n🔗 <a href='https://t.me/{ch[1:]}'>{ch}</a></b>\n\n"
        bot.reply_to(message, msg, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.reply_to(message, "🚫 No channels found.")

# ✅ /signalon
@bot.message_handler(commands=['signalon'])
def signal_on(message):
    global is_signal_on
    if not is_signal_on:
        is_signal_on = True
        threading.Thread(target=prediction_loop).start()
        bot.reply_to(message, "✅ SIGNAL ON COMPLETED")
    else:
        bot.reply_to(message, "⚠️ Already running.")

# ✅ /signaloff
@bot.message_handler(commands=['signaloff'])
def signal_off(message):
    global is_signal_on
    is_signal_on = False
    bot.reply_to(message, "✅ SIGNAL OFF COMPLETED")


if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
