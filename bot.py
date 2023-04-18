import datetime
import os
import random
from collections import defaultdict
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)

import pytz

gm_users = defaultdict(bool)
all_users = set()

def fetch_group_members(bot, chat_id):
    all_members = set()
    offset = 0
    limit = 200

    while True:
        try:
            chat_member = bot.get_chat_member(chat_id=chat_id, user_id=offset)
            username = chat_member.user.username
            if username:
                all_members.add(username)

            offset += 1
        except Exception as e:
            break

    return all_members


def reset_gm_users(context):
    gm_users.clear()

def send_gm(context):
    chat_id = ("-1001854584771")
    context.bot.send_message(chat_id=chat_id, text="GM")
    gif_url = "https://media.tenor.com/y1n4lM9lR_kAAAAM/take-no.gif"
    context.bot.send_animation(chat_id=chat_id, animation=gif_url)


def error_handler(update: Update, context: CallbackContext):
    try:
        raise context.error
    except Unauthorized:
        pass
    except BadRequest:
        pass
    except TimedOut:
        pass
    except NetworkError:
        pass
    except ChatMigrated as e:
        pass
    except TelegramError:
        pass

def gm_command(update: Update, context: CallbackContext):
    send_gm(context)

def start_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="ham ham lecker eisen")

def check_gm(update: Update, context: CallbackContext):
    if update.message is not None:
        user_name = update.message.from_user.username
        message_text = update.message.text

        if message_text.lower() == "gm":
            gm_users[user_name] = True

def check_all_gm_sent(context):
    global all_users
    chat_id = ("-1001854584771")
    missing_users = all_users.difference(set(gm_users.keys()))

    if not missing_users:
        context.bot.send_message(chat_id=chat_id, text="EUCH AUCH EINEN GUTEN MORGEN!")
        photo_url = "https://picr.eu/images/2023/04/18/FpnQl.jpg"
        context.bot.send_photo(chat_id=chat_id, photo=photo_url)
    else:
        message = "Fehlende GM-Nachrichten von: " + ", ".join([f"@{user}" for user in missing_users])
        context.bot.send_message(chat_id=chat_id, text=message)

def send_poem(context):
    chat_id = ("-1001854584771")
    poem = """\
Stahl in den Händen,
Muskeln wachsen, Kraft erwacht,
Körper formen sich.
GN."""
    context.bot.send_message(chat_id=chat_id, text=poem)
    photo_url = "https://picr.eu/images/2023/04/18/Fp87k.jpg"
    context.bot.send_photo(chat_id=chat_id, photo=photo_url)
    
def mention_everyone(context: CallbackContext):
    now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
        if now.weekday() == 6 and now.hour == 12:  # Check if it's Sunday and 12:00
        chat_id = ("-1001854584771")
        # Make sure the fetched users are up-to-date
        global all_users
        all_users = fetch_group_members(context.bot, chat_id)
        mention_list = " ".join([f"@{user}" for user in all_users if user])  # Filter out any None values
        if mention_list:
            context.bot.send_message(chat_id=chat_id, text=f"Es ist Sonntag! Check-In nicht vergessen! {mention_list}")
        else:
            context.bot.send_message(chat_id=chat_id, text=f"Es ist Sonntag! Check-In nicht vergessen!")

def lift_command(update: Update, context: CallbackContext):
    print("lift_command aufgerufen")
    chat_id = ("-1001854584771")
    message_text = update.message.text.partition(' ')[2]
    print(f"message_text: {message_text}")
    message_text = message_text.replace('\n', '  \n')
    if message_text:
        context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bitte geben Sie eine Nachricht nach dem /lift Befehl ein.")

def quote_command1(update: Update, context: CallbackContext):
    print("quote_command1 aufgerufen")
    chat_id = ("-1001854584771")
    quote = """\
I have found the Iron to be my greatest friend. <br>
It never freaks out on me, never runs. <br>
Friends may come and go. <br><br>
But two hundred pounds is always two hundred pounds."""
    context.bot.send_message(chat_id=chat_id, text=quote, parse_mode='HTML')

def send_random_message(context: CallbackContext):
    chat_id = ("-1001854584771")
    message = """\
Im Labyrinth der Seele wandert Michael, <br>
Verloren, suchend, wie ein Schatten blind, <br>
Zerfurcht sein Herz, sein Geist noch unbeständig, <br>
Ein junger Mann, der seinen Weg nicht findet. <br><br>
Der Lebensstürme wilder Tanz umhüllt ihn, <br>
Zerrt ihn hinfort, verweht die Hoffnung fein, <br>
Die Qual der Wahl, die Schatten seiner Zweifel, <br>
Lähmen seinen Geist, gefangen im Sein. <br><br>
Und schließlich kommt er an, am Rand der Welt, <br>
Ein kleines Land, von blauem Meer umspült, <br>
Er dachte, er fände hier das Paradies, <br>
Aber es war Malta, und Malta war ok."""
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

def nako_command(update: Update, context: CallbackContext):
    print("nako_command aufgerufen")
    send_random_message(context)

def calculate_first_run_time(random_weekday, random_hour, random_minute, timezone):
    now = datetime.datetime.now(timezone)
    days_ahead = random_weekday - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_run_time = now + datetime.timedelta(days=days_ahead)
    first_run_time = first_run_time.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    return first_run_time

def command_debug(update: Update, context: CallbackContext):
    print(f"Command: {update.message.text}")
    
def main():
    print("Bot startet...")
    global all_users
    api_token = ("REDACTED_TELEGRAM_TOKEN")
    updater = Updater(api_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    print("start_command registriert")
    dp.add_handler(CommandHandler("lift", lift_command))
    print("lift_command registriert")
    dp.add_handler(CommandHandler("gm", gm_command))
    print("gm_command registriert")
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    print("check_gm registriert")
    dp.add_handler(CommandHandler("rollins", quote_command1, run_async=True))
    print("quote_command1 registriert")
    dp.add_handler(CommandHandler("nako", nako_command, run_async=True))
    print("nako_command registriert")
    dp.add_error_handler(error_handler)
    print("error_handler registriert")
    dp.add_handler(MessageHandler(Filters.command, command_debug))
    dp.add_error_handler(error_handler)
    
    jq = updater.job_queue

    # Zeitzone festlegen
    timezone = pytz.timezone('Europe/Berlin')
    jq.run_daily(send_gm, time=datetime.time(hour=5, tzinfo=timezone))
    jq.run_daily(reset_gm_users, time=datetime.time(hour=0, tzinfo=timezone))
    jq.run_daily(check_all_gm_sent, time=datetime.time(hour=9, tzinfo=timezone))
    jq.run_daily(send_poem, time=datetime.time(hour=22, tzinfo=timezone))
    jq.run_repeating(mention_everyone, interval=datetime.timedelta(hours=1), first=datetime.time(hour=12, tzinfo=timezone))
    
    random_weekday = random.randint(0, 6)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    first_run_time = calculate_first_run_time(random_weekday, random_hour, random_minute, timezone)

    jq.run_repeating(send_random_message, interval=datetime.timedelta(weeks=1), first=first_run_time)
   
    jq.start()

    chat_id = ("-1001854584771")
    all_users = fetch_group_members(dp.bot, chat_id)

    updater.start_polling()
    print("Bot gestartet und Polling")
    updater.idle()
    print("Bot beendet")

if __name__ == '__main__':
    main()
