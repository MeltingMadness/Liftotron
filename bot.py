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
    
def mention_everyone(context):
    chat_id = ("-1001854584771")
    mention_text = " ".join([f"@{user}" for user in all_users])
    message = f"Hey, es ist Sonntag! Zeit für den Check-In! {mention_text}"
    context.bot.send_message(chat_id=chat_id, text=message)

    
def lift_command(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        chat_id = ("-1001854584771")
        text = " ".join(context.args)
        if text:
            context.bot.send_message(chat_id=chat_id, text=text)
        else:
            update.message.reply_text("Bitte füge Text zum /lift Befehl hinzu.")



def main():
    global all_users
    api_token = ("REDACTED_TELEGRAM_TOKEN")
    updater = Updater(api_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    dp.add_error_handler(error_handler)
    dp.add_handler(CommandHandler("lift", lift_command))
    
    jq = JobQueue()
    jq.set_dispatcher(dp)

    # Zeitzone festlegen
    timezone = pytz.timezone('Europe/Berlin')
    jq.run_daily(send_gm, time=datetime.time(hour=5, tzinfo=timezone))
    jq.run_daily(reset_gm_users, time=datetime.time(hour=0, tzinfo=timezone))
    jq.run_daily(check_all_gm_sent, time=datetime.time(hour=9, tzinfo=timezone))
    jq.run_daily(send_poem, time=datetime.time(hour=22, tzinfo=timezone))
    jq.run_daily(mention_everyone, day=(6,), time=datetime.time(hour=12, tzinfo=timezone))
    
    jq.start()

    # Fetch group members
    chat_id = ("-1001854584771")
    all_users = fetch_group_members(dp.bot, chat_id)

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(MessageHandler(Filters.text, check_gm))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater = Updater(api_token, use_context=True, workers=4)
    updater.idle()

if __name__ == '__main__':
    main()
