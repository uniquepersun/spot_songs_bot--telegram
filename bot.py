import os
import telebot
import dotenv
import requests
from telebot import types

dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

log_bot_url = "https://api.telegram.org/bot" + BOT_TOKEN + "/"
log_channel_id = os.environ['LOG_CHANNEL_ID']
promote_channel_username = "@uniqueersun"
promote_channel_link = "https://t.me/uniquepersun"
bot_name = "unique_spot_for_songs"

def log(log_message):
    log = requests.post(log_bot_url + "sendMessage", data={
        "chat_id": log_channel_id,
        "text": log_message
    })
def check_membership(channel, user):
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getChatMember', params={'chat_id': channel, 'user_id': user})
    
    data = response.json()
    if data['ok']:
        member_status = data['result']['status']
        if member_status == 'member' or member_status == 'creator' or member_status == 'administrator':
            print('The user is a member of the channel.')
            return True
        else:
            print('The user is not a member of the channel.')
            return False
    else:
        print('Failed to retrieve member information.')
        return False


def try_to_delete_message(chat_id, message_id):
    bot = telebot.TeleBot(BOT_TOKEN)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

spotify_shortened_link = r'https?:\/\/spotify\.link\/[A-Za-z0-9]+'
spotify_track_link = r'https?:\/\/open\.spotify\.com\/(intl-[a-zA-Z]{2}\/)?track\/[a-zA-Z0-9]+'
spotify_album_link = r'https?:\/\/open\.spotify\.com\/(intl-[a-zA-Z]{2}\/)?album\/[a-zA-Z0-9]+'
spotify_playlist_link = r'https?:\/\/open\.spotify\.com\/(intl-[a-zA-Z]{2}\/)?playlist\/[a-zA-Z0-9]+'
spotify_correct_link = spotify_track_link + "|" + spotify_album_link + "|" + spotify_playlist_link + "|" + spotify_shortened_link

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "hola amigo!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "For any query, see the repository at:https://github.com/uniquepersun")
    
@bot.message_handler(regexp=spotify_correct_link)
def handle_correct_link(message):
    gm1 = bot.send_message(message.chat.id,"Okay, wait and watch..")
    try:
        is_member = check_membership(promote_channel_username, message.chat.id)

        if is_member:
            log(bot_name + " log:\nuser " + str(message.chat.id) + " is member of channel.")
        else:
            log(bot_name + " log:\nuser " + str(message.chat.id) + " is not member of channel.")
            
            # Send message with join button to user
            keyboard = types.InlineKeyboardMarkup()
            channel_button = types.InlineKeyboardButton(text='Join', url=promote_channel_link)
            keyboard.add(channel_button)
            bot.send_message(message.chat.id,"Your link is correct✅.Join to get access to database, then send your link again.",
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            reply_markup=keyboard)

            try_to_delete_message(message.chat.id,"Ok, be patient and wait...".message_id)
            return
        
    except Exception as e:
        try_to_delete_message(message.chat.id,"Okay, be atient and watch".message_id)
        bot.send_message(message.chat.id, "Sorry, my process wasn't sucessful :(But you can try another link or use the bot again after some time, it might help.You can also search for your favorite tracks or artists in my huge [database](https://t.me/+wAztHySpQcdkZjk0)", parse_mode="Markdown")
        log(bot_name + " log:\nA general error occurred: " + str(e))

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
bot.infinity_polling()