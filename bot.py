import datetime
import os
from collections import defaultdict
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)

import pytz

gm_users = defaultdict(bool)

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
    gif_url = "https://media3.giphy.com/media/2IxtjutFAGLfdI1GvK/giphy.gif"
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
        context.bot.send_message(chat_id=chat_id, text="EUCH AUCH EINEN GUTEN MORGEN")
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
    
def mention_everyone(context: CallbackContext):
    now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
    if now.weekday() == 6 and now.hour == 12:  # Check if it's Sunday and 12:00
        chat_id = ("-1001854584771")
        mention_list = " ".join([f"@{user}" for user in all_users])
        context.bot.send_message(chat_id=chat_id, text=f"Es ist Sonntag! Check-In nicht vergessen! {mention_list}")

    
def lift_command(update: Update, context: CallbackContext):
    print("lift_command aufgerufen")  
    chat_id = ("-1001854584771")
    message_text = ' '.join(context.args)
    print(f"message_text: {message_text}")  
    if message_text:
        context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bitte geben Sie eine Nachricht nach dem /lift Befehl ein.")

def main():
    global all_users
    api_token = ("5805275775:AAHGYsqX7dW9pUme8jFKT97xy-i29z5qHfo")
    updater = Updater(api_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("lift", lift_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    dp.add_error_handler(error_handler)
    
    
    jq = JobQueue()
    jq.set_dispatcher(dp)

    # Zeitzone festlegen
    timezone = pytz.timezone('Europe/Berlin')
    jq.run_daily(send_gm, time=datetime.time(hour=5, tzinfo=timezone))
    jq.run_daily(reset_gm_users, time=datetime.time(hour=0, tzinfo=timezone))
    jq.run_daily(check_all_gm_sent, time=datetime.time(hour=9, tzinfo=timezone))
    jq.run_daily(send_poem, time=datetime.time(hour=22, tzinfo=timezone))
    jq.run_repeating(mention_everyone, interval=datetime.timedelta(hours=1), first=datetime.time(hour=12, tzinfo=timezone))
    
    jq.start()

    # Fetch group members
    chat_id = ("-1001854584771")
    all_users = fetch_group_members(dp.bot, chat_id)

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    dp.add_handler(CommandHandler("lift", lift_command))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    # updater = Updater(api_token, use_context=True, workers=4)
    updater.idle()

if __name__ == '__main__':
    main()
