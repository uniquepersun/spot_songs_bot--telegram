import os
import telebot
import dotenv
import requests
from telebot import types
import re
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from bs4 import BeautifulSoup

dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

log_bot_url = "https://api.telegram.org/bot" + BOT_TOKEN + "/"
log_channel_id = os.environ['LOG_CHANNEL_ID']
promote_channel_username = "@uniqueersun"
promote_channel_link = "https://t.me/uniquepersun"
bot_name = "unique_spot_for_songs"
spotify_client_id = os.environ["SPOTIFY_APP_CLIENT_ID"]
spotify_client_secret = os.environ["SPOTIFY_APP_CLIENT_SECRET"]


def log(log_message):
    log = requests.post(log_bot_url + "sendMessage", data={
        "chat_id": log_channel_id,
        "text": log_message
    })
    if log.status_code == 200:
        print('log registered')
    else:
        print('Error in registering log:', log.status_code)

def write_list_to_file(my_list, file_path):
    with open(file_path, 'w') as file:
        for item in my_list:
            file.write(item + '\n')

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

def list_of_files_in_a_folder(folder_path):
    try:
        file_names = os.listdir(folder_path)
        file_names.sort(key=lambda filename: os.path.getctime(os.path.join(folder_path, filename)))
        return file_names
    except FileNotFoundError:
        print(f"Folder {folder_path} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def try_to_delete_message(chat_id, message_id):
    bot = telebot.TeleBot(BOT_TOKEN)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def get_redirect_link(shortened_link):
    response = requests.head(shortened_link, allow_redirects=True)
    return response.url

def get_link_type(text):
    if re.match(spotify_track_link, text):
        return "track"
    elif re.match(spotify_album_link, text):
        return "album"
    elif re.match(spotify_playlist_link, text):
        return "playlist"
    elif re.match(spotify_shortened_link, text):
        return "shortened"
    else:
        return False
def get_valid_spotify_links(text):
    regexes = [spotify_shortened_link, spotify_track_link, spotify_album_link, spotify_playlist_link]
    regex_combined = re.compile("|".join(regexes))
    all_matches = [match.group() for match in regex_combined.finditer(text)]
    print(all_matches)
    return all_matches

def get_track_ids(link):
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    link_id = link.split("/")[-1].split("?")[0]

    link_type = get_link_type(link)
    if link_type == "track":
        tracks = sp.track(link_id)
        track_ids = [tracks["id"]]
    elif link_type == "album":
        tracks = sp.album_tracks(link_id)["items"]
        track_ids = [t["id"] for t in tracks]
    elif link_type == "playlist":
        # handle spotify results paginated in 100 items 
        # https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist
        results = sp.playlist_tracks(link_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        track_ids = []
        for t in tracks:
            try:
                if ("track" in t) and (t["track"] is not None) and ("id" in t["track"]) and (t["track"]["id"] is not None):
                    track_ids.append(t["track"]["id"])
            except:
                print("error in getting a track id")
    else:
        return []

    return(track_ids)

def get_track_image(track_link):
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    track_id = track_link.split("/")[-1].split("?")[0]
    track = sp.track(track_id)
    cover_image_url = track['album']['images'][0]['url']
    
    return cover_image_url


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

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "pong!!")
@bot.message_handler(commands=['search'])
def search_song(message):
    url = "https://open.spotify.com/search/" + message
    a = requests.get(url)
    soup = BeautifulSoup(a.content, 'html.parser')
    b = soup.find('div',{})
    c = soup.find('a',{'class':'XLAiqekZxk4Z7Nok9a58'})
    keyboard = types.InlineKeyboardButton(b)
    try_to_delete_message(message.chat.id, "Okay, wait and watch".message_id)
    return
    
@bot.message_handler(regexp=spotify_correct_link)
def handle_correct_link(message):
    gm1 = bot.send_message(message.chat.id,"Okay, wait and watch..")
    try:
        is_member = check_membership(promote_channel_username, message.chat.id)

        if is_member:
            log(bot_name + " log:\nuser " + str(message.chat.id) + " is member of channel.")
        else:
            log(bot_name + " log:\nuser " + str(message.chat.id) + " is not member of channel.")
            
            keyboard = types.InlineKeyboardMarkup()
            channel_button = types.InlineKeyboardButton(text='Join', url=promote_channel_link)
            keyboard.add(channel_button)
            bot.send_message(message.chat.id,"Your link is correct✅.Join to get access to database, then send your link again.",
                            parse_mode="Markdown",
                            disable_web_page_preview=True,
                            reply_markup=keyboard)

            try_to_delete_message(message.chat.id,gm1.message_id)
            return
        
        valid_spotify_links_in_user_text = get_valid_spotify_links(message.text)
        first_link = valid_spotify_links_in_user_text[0]
        if get_link_type(first_link) == "shortened":
            log(bot_name + " log:\nshortened link sent from user: " + str(message.chat.id))
            first_link = get_redirect_link(first_link)
            
        link_type = get_link_type(first_link)
        if link_type not in ["track", "album", "playlist"]:
            try_to_delete_message(message.chat.id, gm1.message_id)
            bot.send_message(message.chat.id, "Looks like this link is wrong, expired or not supported. Try another.")
            log(bot_name + " log:\nerror in handling short link.")
            return
        
        matches = get_track_ids(first_link)
        
        if len(matches) > 1000:
            try_to_delete_message(message.chat.id, gm1.message_id)
            bot.send_message(message.chat.id, "Bot can't download playlists more than 1000 tracks at the moment.\This feature will be added later.")
            log(bot_name + " log:\nPlaylist more than 1000 tracks from user: " + str(message.chat.id))
            return

        if not matches:
            try_to_delete_message(message.chat.id, gm1.message_id)
            bot.send_message(message.chat.id, "sorry I couldn't extract tracks from link.")
            log(bot_name + " log:\nZero tracks error from user: " + str(message.chat.id))
            return
        
        for folder in ["track", "album", "playlist"]:
            folder_path = "./received_links" + "/" + folder
            files = list_of_files_in_a_folder(folder_path)
            if str(message.chat.id) in files:
                try_to_delete_message(message.chat.id, gm1.message_id)
                bot.send_message(message.chat.id, "work already in progress, waittt!", parse_mode="Markdown", disable_web_page_preview=True)
                log(bot_name + " log:\nalready sth to download\nuser: " + str(message.chat.id))
                return
        
        write_list_to_file(matches, "./received_links" + "/" + link_type + "/" + str(message.chat.id))

    except Exception as e:
        try_to_delete_message(message.chat.id,gm1.message_id)
        bot.send_message(message.chat.id, "Sorry, my process wasn't sucessful :(But you can try another link or use the bot again after some time, it might help.", parse_mode="Markdown")
        log(bot_name + " log:\nA general error occured: " + str(e))

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text, disable_web_page_preview=True)
    log(bot_name + " log:\n❌wrong link pattern from user: " + str(message.chat.id) + " with contents of:\n" + message.text)

def main():
    bot.infinity_polling()

if __name__ == '__main__':
    main()