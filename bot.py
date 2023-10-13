import datetime
import os
import random
import logging
from collections import defaultdict
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
import pytz

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

class BotState:
    def __init__(self):
        self.gm_users = defaultdict(bool)
        self.all_users = set()

    def fetch_group_members(self, bot, chat_id):
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

        self.all_users = all_members

bot_state = BotState()

def send_gm(context):
    chat_id = ("-1001854584771")
    context.bot.send_message(chat_id=chat_id, text="GM")
    gif_url = "https://media.tenor.com/y1n4lM9lR_kAAAAM/take-no.gif"
    context.bot.send_animation(chat_id=chat_id, animation=gif_url)


def reset_gm_users(context):
    global bot_state
    bot_state.gm_users.clear()

def error_handler(update: Update, context: CallbackContext):
    try:
        raise context.error
    except (Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError):
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
    global bot_state
    chat_id = ("-1001854584771")

    logger.info(f"all_users: {bot_state.all_users}")
    logger.info(f"gm_users.keys(): {set(bot_state.gm_users.keys())}")

    bot_state.fetch_group_members(context.bot, chat_id)
    
    missing_users = bot_state.all_users.difference(set(bot_state.gm_users.keys()))
    
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
    # Replace newline characters with Markdown-compatible line breaks
    message_text = message_text.replace('\n', '  \n')
    if message_text:
        # Use MarkdownV2 as the parse_mode
        context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode='MarkdownV2')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bitte geben Sie eine Nachricht nach dem /lift Befehl ein.")


def quote_command1(update: Update, context: CallbackContext):
    logger.info("quote_command1 called")
    chat_id = ("-1001854584771")
    quote = "I have found the Iron to be my greatest friend.\n" \
            "It never freaks out on me, never runs.\n" \
            "Friends may come and go.\n\n" \
            "But two hundred pounds is always two hundred pounds."
    try:
        context.bot.send_message(chat_id = ("-1001854584771"), text=quote, parse_mode='MarkdownV2')
    except Exception as e:
        logger.error(f"Error in quote_command1: {e}")

def nako_command(update: Update, context: CallbackContext):
    print("nako_command aufgerufen")
    chat_id = ("-1001854584771")
    send_random_message_for_nako(context, chat_id)

def nako_command(update: Update, context: CallbackContext):
    logger.info("nako_command called")
    chat_id = ("-1001854584771")
    message = "Im Labyrinth der Seele wandert Michael,\n" \
              "Verloren, suchend, wie ein Schatten blind,\n" \
              "Zerfurcht sein Herz, sein Geist noch unbeständig,\n" \
              "Ein junger Mann, der seinen Weg nicht findet.\n\n" \
              "Der Lebensstürme wilder Tanz umhüllt ihn,\n" \
              "Zerrt ihn hinfort, verweht die Hoffnung fein,\n" \
              "Die Qual der Wahl, die Schatten seiner Zweifel,\n" \
              "Lähmen seinen Geist, gefangen im Sein.\n\n" \
              "Und schließlich kommt er an, am Rand der Welt,\n" \
              "Ein kleines Land, von blauem Meer umspült,\n" \
              "Er dachte, er fände hier das Paradies,\n" \
              "Aber es war Malta, und Malta war ok."
    try:
        context.bot.send_message(chat_id = ("-1001854584771"), text=message, parse_mode='MarkdownV2')
    except Exception as e:
        logger.error(f"Error in nako_command: {e}")

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
    # Main code here
    print("Bot is starting...")
    
    # Initialize your bot, dispatcher, and job queue
    updater = Updater("REDACTED_TELEGRAM_TOKEN", use_context=True)
    dp = updater.dispatcher
    jq = updater.job_queue

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("lift", lift_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    dp.add_handler(CommandHandler("rollins", quote_command1))
    dp.add_handler(CommandHandler("nako", nako_command))
    dp.add_error_handler(error_handler)

    # Timezone
    timezone = pytz.timezone('Europe/Berlin')

    # Schedule jobs
    jq.run_daily(send_gm, time=datetime.time(hour=5, tzinfo=timezone))
    jq.run_daily(reset_gm_users, time=datetime.time(hour=0, tzinfo=timezone))
    jq.run_daily(check_all_gm_sent, time=datetime.time(hour=9, tzinfo=timezone))
    jq.run_daily(send_poem, time=datetime.time(hour=22, tzinfo=timezone))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

