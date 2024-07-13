import os
import telebot
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "hola amigo!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "For any query, see the repository at:https://github.com/uniquepersun")
    
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
bot.infinity_polling()