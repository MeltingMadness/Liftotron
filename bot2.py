import datetime
import os
import random
import logging
from collections import defaultdict

import pytz
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Konstanten (wie Chat-ID und Token) bleiben hardcodiert, wie gewünscht
CHAT_ID = "-1001854584771"
BOT_TOKEN = "REDACTED_TELEGRAM_TOKEN"

class BotState:
    def __init__(self):
        # Speichert, welche User bereits ihre GM gesendet haben (username: bool)
        self.gm_users = defaultdict(bool)
        # Speichert bekannte User des Chats (z. B. Admins und alle, die interagiert haben)
        self.all_users = set()

    def fetch_group_members(self, bot, chat_id):
        """
        Versucht, über get_chat_administrators (und ggf. andere Quellen) bekannte
        Mitglieder abzurufen und in self.all_users zu speichern.
        Aufgrund von Einschränkungen der Telegram API wird hier nur eine Teilmenge
        (z. B. Administratoren) erfasst.
        """
        try:
            admins = bot.get_chat_administrators(chat_id)
            for admin in admins:
                username = admin.user.username
                if username:
                    self.all_users.add(username)
        except Exception as e:
            logger.error("Fehler beim Abrufen der Chat-Administratoren: %s", e)
        # Hinweis: Zusätzlich fügen wir in check_gm alle Nutzer hinzu, die interagieren.

# Initialer Zustand des Bots
bot_state = BotState()


def send_gm(context: CallbackContext):
    """
    Sendet die tägliche GM-Nachricht (und eine Animation) an den Chat.
    """
    context.bot.send_message(chat_id=CHAT_ID, text="GM")
    gif_url = "https://media.tenor.com/y1n4lM9lR_kAAAAM/take-no.gif"
    context.bot.send_animation(chat_id=CHAT_ID, animation=gif_url)


def reset_gm_users(context: CallbackContext):
    """
    Setzt die Liste der GM-senden Nutzer zurück.
    """
    bot_state.gm_users.clear()
    logger.info("GM-Status wurde zurückgesetzt.")


def error_handler(update: Update, context: CallbackContext):
    """
    Zentrale Fehlerbehandlung: Loggt Fehler und unterdrückt bekannte Ausnahmen.
    """
    try:
        raise context.error
    except (Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError) as e:
        logger.error("TelegramError: %s", e)


def gm_command(update: Update, context: CallbackContext):
    """
    /gm-Befehl: Löst die GM-Aktion aus.
    """
    send_gm(context)


def start_command(update: Update, context: CallbackContext):
    """
    /start-Befehl: Begrüßt den Nutzer.
    """
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="ham ham lecker eisen")


def check_gm(update: Update, context: CallbackContext):
    """
    Überprüft, ob der Nachrichteninhalt "gm" (unabhängig von Groß-/Kleinschreibung)
    lautet. Falls ja, wird der User als 'GM gesendet' markiert und in die all_users-Liste aufgenommen.
    """
    if update.message is not None:
        user = update.message.from_user
        username = user.username
        message_text = update.message.text

        if message_text.lower() == "gm" and username:
            bot_state.gm_users[username] = True
            # Ergänzt all_users mit jedem, der interagiert – so kennen wir zumindest aktive User
            bot_state.all_users.add(username)
            logger.info("User @%s hat gm gesendet.", username)


def check_all_gm_sent(context: CallbackContext):
    """
    Um 09:00 Uhr wird geprüft, ob alle bekannten Nutzer (in bot_state.all_users)
    ihre GM-Nachricht gesendet haben. Bei vollständiger Beteiligung wird ein Gruß inklusive Foto gesendet,
    andernfalls eine Liste der fehlenden Nutzer.
    """
    logger.info("Bekannte User: %s", bot_state.all_users)
    logger.info("GM-User: %s", set(bot_state.gm_users.keys()))

    # Aktualisiere die bekannten User (z. B. aus der Admin-Liste)
    bot_state.fetch_group_members(context.bot, CHAT_ID)

    missing_users = bot_state.all_users.difference(set(bot_state.gm_users.keys()))

    if not missing_users:
        context.bot.send_message(chat_id=CHAT_ID, text="EUCH AUCH EINEN GUTEN MORGEN!")
        photo_url = "https://picr.eu/images/2023/04/18/FpnQl.jpg"
        context.bot.send_photo(chat_id=CHAT_ID, photo=photo_url)
    else:
        message = "Fehlende GM-Nachrichten von: " + ", ".join([f"@{user}" for user in missing_users])
        context.bot.send_message(chat_id=CHAT_ID, text=message)


def send_poem(context: CallbackContext):
    """
    Sendet abends ein Gedicht zusammen mit einem Bild.
    """
    poem = (
        "Stahl in den Händen,\n"
        "Muskeln wachsen, Kraft erwacht,\n"
        "Körper formen sich.\n"
        "GN."
    )
    context.bot.send_message(chat_id=CHAT_ID, text=poem)
    photo_url = "https://picr.eu/images/2023/04/18/Fp87k.jpg"
    context.bot.send_photo(chat_id=CHAT_ID, photo=photo_url)


def mention_everyone(context: CallbackContext):
    """
    Beispiel-Funktion, die (falls benötigt) alle bekannten User erwähnt.
    Beachten Sie, dass hier nur die in bot_state.all_users gespeicherten Nutzer erwähnt werden.
    """
    now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
    if now.weekday() == 6 and now.hour == 12:  # Sonntag, 12:00
        # Aktualisiere bekannte User (z. B. Admins)
        bot_state.fetch_group_members(context.bot, CHAT_ID)
        mention_list = " ".join([f"@{user}" for user in bot_state.all_users if user])
        if mention_list:
            context.bot.send_message(chat_id=CHAT_ID, text=f"Es ist Sonntag! Check-In nicht vergessen! {mention_list}")
        else:
            context.bot.send_message(chat_id=CHAT_ID, text=f"Es ist Sonntag! Check-In nicht vergessen!")


def lift_command(update: Update, context: CallbackContext):
    """
    /lift-Befehl: Sendet eine Nachricht (möglicherweise als "Lift"-Message) an den Chat.
    Der Text wird als MarkdownV2 formatiert.
    """
    logger.info("lift_command aufgerufen")
    message_text = update.message.text.partition(' ')[2]
    logger.info("Nachrichtentext: %s", message_text)
    # Ersetze Zeilenumbrüche durch Markdown-kompatible Zeilenumbrüche
    message_text = message_text.replace('\n', '  \n')
    if message_text:
        try:
            context.bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode='MarkdownV2')
        except Exception as e:
            logger.error("Fehler in lift_command: %s", e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Bitte geben Sie eine Nachricht nach dem /lift Befehl ein.")


def quote_command1(update: Update, context: CallbackContext):
    """
    /rollins-Befehl: Sendet ein fest vorgegebenes Zitat.
    """
    quote = (
        "I have found the Iron to be my greatest friend.\n"
        "It never freaks out on me, never runs.\n"
        "Friends may come and go.\n"
        "But two hundred pounds is always two hundred pounds."
    )
    try:
        context.bot.send_message(chat_id=CHAT_ID, text=quote)
    except Exception as e:
        logger.error("Error in quote_command1: %s", e)


def nako_command(update: Update, context: CallbackContext):
    """
    /nako-Befehl: Sendet einen vorgefertigten poetischen Text.
    """
    message = (
        "Im Labyrinth der Seele wandert Michael,\n"
        "Verloren, suchend, wie ein Schatten blind,\n"
        "Zerfurcht sein Herz, sein Geist noch unbeständig,\n"
        "Ein junger Mann, der seinen Weg nicht findet.\n\n"
        "Der Lebensstürme wilder Tanz umhüllt ihn,\n"
        "Zerrt ihn hinfort, verweht die Hoffnung fein,\n"
        "Die Qual der Wahl, die Schatten seiner Zweifel,\n"
        "Lähmen seinen Geist, gefangen im Sein.\n\n"
        "Und schließlich kommt er an, am Rand der Welt,\n"
        "Ein kleines Land, von blauem Meer umspült,\n"
        "Er dachte, er fände hier das Paradies,\n"
        "Aber es war Malta, und Malta war ok."
    )
    try:
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error("Error in nako_command: %s", e)


def calculate_first_run_time(random_weekday, random_hour, random_minute, timezone):
    """
    Berechnet den Zeitpunkt für den ersten Job-Lauf, basierend auf einem zufälligen
    Wochentag und einer zufälligen Uhrzeit im angegebenen Zeitzonen-Kontext.
    """
    now = datetime.datetime.now(timezone)
    days_ahead = random_weekday - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_run_time = now + datetime.timedelta(days=days_ahead)
    first_run_time = first_run_time.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    return first_run_time


def command_debug(update: Update, context: CallbackContext):
    """
    Einfacher Debug-Befehl, der den empfangenen Befehl in der Konsole ausgibt.
    """
    logger.info("Command received: %s", update.message.text)


def main():
    logger.info("Bot wird gestartet...")
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    jq = updater.job_queue

    # Handler für Befehle und Nachrichten
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("lift", lift_command))
    dp.add_handler(CommandHandler("gm", gm_command))
    dp.add_handler(CommandHandler("rollins", quote_command1))
    dp.add_handler(CommandHandler("nako", nako_command))
    dp.add_handler(CommandHandler("debug", command_debug))
    dp.add_handler(MessageHandler(Filters.text, check_gm))
    dp.add_error_handler(error_handler)

    # Zeitzone: Europe/Berlin
    timezone = pytz.timezone('Europe/Berlin')

    # Geplante Jobs:
    jq.run_daily(send_gm, time=datetime.time(hour=5, tzinfo=timezone))
    jq.run_daily(reset_gm_users, time=datetime.time(hour=0, tzinfo=timezone))
    jq.run_daily(check_all_gm_sent, time=datetime.time(hour=9, tzinfo=timezone))
    jq.run_daily(send_poem, time=datetime.time(hour=22, tzinfo=timezone))
    # Falls gewünscht, kann mention_everyone ebenfalls als Job eingereiht werden:
    # jq.run_daily(mention_everyone, time=datetime.time(hour=12, minute=0, tzinfo=timezone))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
