import os
import threading
import time
import uuid
from flask import Flask
import telebot
from telebot import types

# خواندن توکن از متغیر محیطی (امنیت کامل در گیت‌هاب)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8920570131

app = Flask("")


@app.route("/")
def home():
  return "Dark Don Bot is active 24/7! 🧠🔥"


def run_web():
  app.run(host="0.0.0.0", port=10000)


bot = telebot.TeleBot(TOKEN) if TOKEN else None

# حافظه‌های موقت
ADMIN_UNLOCKED = set()
FILE_DATABASE = {}
BOT_USERNAME = ""

if bot:
  try:
    BOT_USERNAME = bot.get_me().username
  except Exception:
    BOT_USERNAME = "DarkDonBot"

if bot:

  @bot.message_handler(commands=["start"])
  def send_welcome(message):
    global BOT_USERNAME
    if not BOT_USERNAME:
      try:
        BOT_USERNAME = bot.get_me().username
      except Exception:
        BOT_USERNAME = "DarkDonBot"

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    # بررسی دیپ‌لینک فایل (برای کاربران عمومی)
    if len(text.split()) > 1:
      arg = text.split()[1]
      if arg.startswith("file_"):
        file_code = arg.replace("file_", "")
        if file_code in FILE_DATABASE:
          file_info = FILE_DATABASE[file_code]
          file_id = file_info["file_id"]
          file_type = file_info["type"]

          # ۱. ارسال هشدار دقیق
          bot.send_message(
              chat_id,
              "⚠️ **هشدار:** فایل بالایی پاک میشه لطفاً فایل رو به Save"
              " Massage خودتو هدایت کنید! 🧠",
              parse_mode="Markdown",
          )

          # ۲. ارسال فایل اصلی
          sent_msg = None
          if file_type == "document":
            sent_msg = bot.send_document(chat_id, file_id)
          elif file_type == "video":
            sent_msg = bot.send_video(chat_id, file_id)
          elif file_type == "audio":
            sent_msg = bot.send_audio(chat_id, file_id)
          elif file_type == "photo":
            sent_msg = bot.send_photo(chat_id, file_id)

          if sent_msg:
            # ۳. حلقه هوشمند حذف فایل بعد از ۱۵ ثانیه با تلاش مداوم (Retry Loop)
            def auto_delete_file():
              time.sleep(15)
              while True:
                try:
                  bot.delete_message(chat_id, sent_msg.message_id)
                  break
                except Exception:
                  time.sleep(2)

            threading.Thread(target=auto_delete_file, daemon=True).start()
          return
        else:
          bot.reply_to(
              message,
              "❌ این لینک منقضی شده یا وجود ندارد.",
              parse_mode="Markdown",
          )
          return

    # استارت معمولی در پیوی
    if user_id == ADMIN_ID:
      bot.reply_to(
          message,
          "سلام ارباب دارک دان! 🧠🖤\nبرای فعال‌سازی پنل مدیریت، **توکن بات**"
          " رو برام بفرست.",
      )
    else:
      bot.reply_to(
          message,
          "سلام! من **دارک دان** هستم 🧠\nبرای دریافت فایل از طریق لینک‌های"
          " کانال اقدام کنید.",
      )

  # پردازش پیام‌های ادمین در پیوی
  @bot.message_handler(
      func=lambda m: m.chat.type == "private" and m.from_user.id == ADMIN_ID
  )
  def handle_admin_private(message):
    global BOT_USERNAME
    if not BOT_USERNAME:
      try:
        BOT_USERNAME = bot.get_me().username
      except Exception:
        BOT_USERNAME = "DarkDonBot"

    user_text = message.text.strip() if message.text else ""

    # شناسایی توکن بات توسط مالک برای باز شدن پنل کنترل
    if user_text == TOKEN:
      ADMIN_UNLOCKED.add(ADMIN_ID)
      bot.reply_to(
          message,
          "🔓 **پنل کنترل مالک (دارک دان) با موفقیت فعال شد!** 🧠🔥\n\nحالا هر"
          " فایلی که می‌خواهی براش لینک بسازی رو برام بفرست.",
          parse_mode="Markdown",
      )
      return

    # اگر پنل ادمین فعال است و فایل فرستاده است
    if ADMIN_ID in ADMIN_UNLOCKED:
      file_id = None
      file_type = None

      if message.content_type == "document":
        file_id = message.document.file_id
        file_type = "document"
      elif message.content_type == "video":
        file_id = message.video.file_id
        file_type = "video"
      elif message.content_type == "audio":
        file_id = message.audio.file_id
        file_type = "audio"
      elif message.content_type == "photo":
        file_id = message.photo[-1].file_id
        file_type = "photo"

      if file_id:
        file_code = str(uuid.uuid4())[:8]  # کد یکتا
        FILE_DATABASE[file_code] = {"file_id": file_id, "type": file_type}

        deep_link = f"https://t.me/{BOT_USERNAME}?start=file_{file_code}"
        bot.reply_to(
            message,
            f"✅ **لینک اختصاصی فایل استخراج شد!**\n\n🔗 لینک کانال:\n`{deep_link}`\n\nکاربر"
            " با کلیک روی لینک میاد پیوی، هشدار دریافت می‌کنه، فایل براش ارسال"
            " میشه و بعد از ۱۵ ثانیه با تلاش مداوم پاک میشه! 🧠🔥",
            parse_mode="Markdown",
        )
        return
      else:
        bot.reply_to(
            message,
            "ارباب پنلت فعاله، فایلی که می‌خواهی براش لینک بسازم رو بفرست 🧠",
        )
        return

    # اگر ادمین هنوز توکن رو نفرستاده بود
    bot.reply_to(
        message,
        "⚠️ لطفاً برای فعال‌سازی پنل، اول **توکن بات** رو برام بفرست 🧠",
    )


if __name__ == "__main__":
  t = Thread(target=run_web)
  t.daemon = True
  t.start()

  if bot:
    try:
      bot.remove_webhook(drop_pending_updates=True)
    except Exception:
      pass

    print("Dark Don Bot started successfully 24/7! 🧠")
    bot.infinity_polling()