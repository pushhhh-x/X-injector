import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask, request

# 🔹 Bot & Admin Setup
import os
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
UPI_ID = os.getenv("UPI_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

# ✅ Start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("₹10"), KeyboardButton("₹50"), KeyboardButton("₹100"))
    bot.send_message(chat_id, "🔹 Kaunsa plan lena hai?", reply_markup=markup)

# ✅ Amount Selection
@bot.message_handler(func=lambda msg: msg.text in ["₹10", "₹50", "₹100"])
def ask_mobile_number(message):
    chat_id = message.chat.id
    amount = message.text.replace("₹", "")
    user_data[chat_id] = {"amount": amount}
    bot.send_message(chat_id, "📱 Jis mobile number pe chahiye, wo bhejo:")

# ✅ Mobile Number Input
@bot.message_handler(func=lambda msg: msg.chat.id in user_data and "mobile" not in user_data[msg.chat.id])
def generate_qr(message):
    chat_id = message.chat.id
    user_data[chat_id]["mobile"] = message.text
    amount = user_data[chat_id]["amount"]
    qr_link = f"upi://pay?pa={UPI_ID}&pn=YourName&am={amount}&cu=INR"

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Successful Payment"), KeyboardButton("❌ Cancel Payment"))
    bot.send_message(chat_id, f"📌 Scan this QR to pay ₹{amount}:\n{qr_link}", reply_markup=markup)

# ✅ Payment Confirmation
@bot.message_handler(func=lambda msg: msg.text == "✅ Successful Payment")
def ask_utr(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📝 Payment UTR number bhejo:")

# ✅ UTR Entry
@bot.message_handler(func=lambda msg: msg.chat.id in user_data and "utr" not in user_data[msg.chat.id])
def confirm_payment(message):
    chat_id = message.chat.id
    user_data[chat_id]["utr"] = message.text
    amount = user_data[chat_id]["amount"]
    mobile = user_data[chat_id]["mobile"]
    utr = user_data[chat_id]["utr"]
    
    bot.send_message(ADMIN_ID, f"💰 Payment Request:\n📱 Mobile: {mobile}\n💵 Amount: ₹{amount}\n🔢 UTR: {utr}\n\n✅ Confirm? Reply: /confirm {chat_id}")
    bot.send_message(chat_id, "⏳ Payment verification under process...")

# ✅ Admin Confirmation (/confirm CHAT_ID)
@bot.message_handler(commands=['confirm'])
def send_link(message):
    try:
        chat_id = int(message.text.split()[1])
        bot.send_message(chat_id, "✅ Payment verified! Here is your link: https://yourlink.com")
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
