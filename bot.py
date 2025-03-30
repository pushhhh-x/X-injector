import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

# ✅ Secure Bot & Admin Setup
TOKEN = os.getenv("TOKEN")  # ⚠️ Apne bot ka token Render me store karo
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ⚠️ Apna admin ID bhi Render me store karo
QR_FILE_ID = os.getenv("QR_FILE_ID")  # ⚠️ Apne QR Code ka Telegram File ID bhi hide rakho

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ✅ Start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Pay ₹160"))
    bot.send_message(chat_id, "🔹 Payment ke liye button dabao:", reply_markup=markup)

# ✅ Fixed ₹160 Payment + QR Code
@bot.message_handler(func=lambda msg: msg.text == "✅ Pay ₹160")
def send_qr(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"amount": "160"}

    bot.send_photo(chat_id, QR_FILE_ID, caption="📌 Scan this QR to pay ₹160\n\n✅ Payment hone ke baad 'Payment Done' button dabao.")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Payment Done"), KeyboardButton("❌ Cancel Payment"))
    bot.send_message(chat_id, "🔹 Payment hone ke baad confirm karo:", reply_markup=markup)

# ✅ Payment Confirmation
@bot.message_handler(func=lambda msg: msg.text == "✅ Payment Done")
def ask_payment_proof(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Payment ka screenshot upload karo:")

# ✅ Handle Screenshot Upload
@bot.message_handler(content_types=['photo'])
def receive_screenshot(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "⚠️ Pehle payment ka option use karo!")
        return

    # ✅ Save Screenshot ID
    photo_id = message.photo[-1].file_id
    user_data[chat_id]["screenshot"] = photo_id

    bot.send_message(chat_id, "📝 Ab UPI ID send karo jo payment receipt pe dikh raha hai:")

# ✅ UPI ID Entry & Admin Notification
@bot.message_handler(func=lambda msg: msg.chat.id in user_data and "upi" not in user_data[msg.chat.id])
def confirm_payment(message):
    chat_id = message.chat.id
    user_data[chat_id]["upi"] = message.text  # ✅ UPI ID Store Karo
    amount = user_data[chat_id]["amount"]
    upi = user_data[chat_id]["upi"]
    screenshot = user_data[chat_id]["screenshot"]

    # ✅ Admin Ko Proper Message Send Karo
    bot.send_photo(ADMIN_ID, screenshot, caption=f"""
💰 *New Payment Request*  
💵 Amount: ₹{amount}  
🏦 UPI ID: `{upi}`  
🆔 User ID: `{chat_id}`  
✅ Confirm? Reply: `/confirm {chat_id}`
""", parse_mode="Markdown")

    bot.send_message(chat_id, "⏳ Payment verification under process...")

# ✅ Admin Confirmation (/confirm CHAT_ID)
@bot.message_handler(commands=['confirm'])
def send_link(message):
    try:
        chat_id = int(message.text.split()[1])
        bot.send_message(chat_id, "✅ Payment verified! Here is your link: https://yourlink.com")

        # 🔹 Payment verify hone ke baad firse /start button bhejna
        start_message(type("obj", (object,), {"chat": type("chat", (object,), {"id": chat_id})}))

        bot.send_message(ADMIN_ID, "✅ Payment confirmed and link sent!")
    except:
        bot.send_message(ADMIN_ID, "⚠️ Invalid format! Use: /confirm USER_CHAT_ID")

# ✅ Cancel Payment
@bot.message_handler(func=lambda msg: msg.text == "❌ Cancel Payment")
def cancel_payment(message):
    chat_id = message.chat.id
    user_data.pop(chat_id, None)
    bot.send_message(chat_id, "❌ Payment cancelled!")

# ✅ Run Bot
bot.polling()
