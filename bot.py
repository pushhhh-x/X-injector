import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import qrcode
from io import BytesIO
import os

# 🔹 Bot & Admin Setup
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
UPI_ID = os.getenv("UPI_ID")

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ✅ Start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("₹10"), KeyboardButton("₹50"), KeyboardButton("₹100"))
    bot.send_message(chat_id, "🔹 Kaunsa plan lena hai?", reply_markup=markup)

# ✅ Amount Selection & QR Code Generate
@bot.message_handler(func=lambda msg: msg.text in ["₹10", "₹50", "₹100"])
def generate_qr(message):
    chat_id = message.chat.id
    amount = message.text.replace("₹", "")
    user_data[chat_id] = {"amount": amount}
    upi_link = f"upi://pay?pa={UPI_ID}&pn=YourName&am={amount}&cu=INR"

    # 🔹 QR Code Generate Karo
    qr = qrcode.make(upi_link)
    img_io = BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Successful Payment"), KeyboardButton("❌ Cancel Payment"))

    # ✅ QR Code Image ke saath send karo
    bot.send_photo(chat_id, img_io, caption=f"📌 *Scan this QR to pay ₹{amount}:*", parse_mode="Markdown", reply_markup=markup)

# ✅ Payment Confirmation
@bot.message_handler(func=lambda msg: msg.text == "✅ Successful Payment")
def ask_upi(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📝 Payment hone ke baad jo UPI ID dikh raha hai, wo bhejo:")

# ✅ UPI ID Entry & Admin Notification
@bot.message_handler(func=lambda msg: msg.chat.id in user_data and "upi" not in user_data[msg.chat.id])
def confirm_payment(message):
    chat_id = message.chat.id
    user_data[chat_id]["upi"] = message.text  # ✅ UPI ID Store Karo
    amount = user_data[chat_id]["amount"]
    upi = user_data[chat_id]["upi"]
    
    # ✅ Admin Ko Proper Message Send Karo
    bot.send_message(ADMIN_ID, f"""
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
