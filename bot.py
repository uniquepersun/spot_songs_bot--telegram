import os
import telebot
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(BOT_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)
