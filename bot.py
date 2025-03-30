import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

# 🔹 Bot & Admin Setup
TOKEN = os.getenv("TOKEN")  # ⚠️ Apne bot ka token yaha dalna
ADMIN_ID = os.getenv("ADMIN_ID")  # ⚠️ Apna admin ID dalna

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ✅ Start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Pay ₹160"))
    bot.send_message(chat_id, "🔹 Payment ke liye button dabao:", reply_markup=markup)

# ✅ Fixed ₹160 Payment + Static QR Code
@bot.message_handler(func=lambda msg: msg.text == "✅ Pay ₹160")
def send_qr(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"amount": "160"}
    
    # ⚠️ Apna QR Code yaha upload karke path dalna
    qr_code_path = "https://drive.google.com/file/d/11QQdUCboWCK2_nl0uE_DxVaEi92AB4IF/view?usp=share_link"  # 🔹 Apna QR link dal
    bot.send_photo(chat_id, qr_code_path, caption="📌 Scan this QR to pay ₹160\n\n✅ Payment hone ke baad 'Payment Done' button dabao.")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Payment Done"), KeyboardButton("❌ Cancel Payment"))
    bot.send_message(chat_id, "🔹 Payment hone ke baad confirm karo:", reply_markup=markup)

# ✅ Payment Confirmation
@bot.message_handler(func=lambda msg: msg.text == "✅ Payment Done")
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
