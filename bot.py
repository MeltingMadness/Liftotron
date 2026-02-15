from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import time as day_time
from types import TracebackType
from typing import Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MARKDOWN_V2_SPECIAL_CHARS = "_*[]()~`>#+-=|{}.!"
CONFIG_KEY = "config"
TRACKER_KEY = "gm_tracker"


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True)
class BotConfig:
    bot_token: str
    chat_id: int
    allowed_chat_ids: set[int]
    allowed_user_ids: set[int] | None
    timezone: str


class GMTracker:
    """Tracks known participants and who already sent a daily GM message."""

    def __init__(self, static_user_ids: set[int] | None = None) -> None:
        user_ids = static_user_ids or set()
        self.static_participants = {self.participant_key(user_id, None) for user_id in user_ids}
        self.active_participants: set[str] = set()
        self.gm_users: set[str] = set()

    @staticmethod
    def participant_key(user_id: int | None, username: str | None) -> str:
        if username:
            return username
        if user_id is None:
            return "unknown"
        return f"id:{int(user_id)}"

    def record_activity(self, user_id: int | None, username: str | None) -> None:
        participant = self.participant_key(user_id, username)
        if participant != "unknown":
            self.active_participants.add(participant)

    def record_gm(self, user_id: int | None, username: str | None) -> None:
        participant = self.participant_key(user_id, username)
        if participant != "unknown":
            self.active_participants.add(participant)
            self.gm_users.add(participant)

    def get_missing_participants(self) -> list[str]:
        participants = self.static_participants | self.active_participants
        return sorted(participants - self.gm_users)

    def reset_daily(self) -> None:
        self.gm_users.clear()


def _require_env_value(env: Mapping[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {key}")
    return value


def _parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"{field_name} must be an integer, got: {value!r}") from exc


def _parse_int_csv(value: str, field_name: str) -> set[int]:
    parsed: set[int] = set()
    for raw_item in value.split(","):
        item = raw_item.strip()
        if not item:
            continue
        parsed.add(_parse_int(item, field_name))
    return parsed


def load_config_from_env(env: Mapping[str, str] | None = None) -> BotConfig:
    source = env if env is not None else os.environ
    bot_token = _require_env_value(source, "BOT_TOKEN")
    chat_id = _parse_int(_require_env_value(source, "CHAT_ID"), "CHAT_ID")
    allowed_chat_ids = _parse_int_csv(_require_env_value(source, "ALLOWED_CHAT_IDS"), "ALLOWED_CHAT_IDS")
    if not allowed_chat_ids:
        raise ConfigError("ALLOWED_CHAT_IDS must include at least one chat id")

    allowed_user_ids_raw = source.get("ALLOWED_USER_IDS", "").strip()
    allowed_user_ids = (
        _parse_int_csv(allowed_user_ids_raw, "ALLOWED_USER_IDS") if allowed_user_ids_raw else None
    )

    timezone = source.get("TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"TIMEZONE is invalid: {timezone!r}") from exc

    return BotConfig(
        bot_token=bot_token,
        chat_id=chat_id,
        allowed_chat_ids=allowed_chat_ids,
        allowed_user_ids=allowed_user_ids,
        timezone=timezone,
    )


def is_authorized_update(update: object, config: BotConfig) -> bool:
    chat = getattr(update, "effective_chat", None)
    user = getattr(update, "effective_user", None)

    chat_id = getattr(chat, "id", None)
    if chat_id is None:
        return False
    if int(chat_id) not in config.allowed_chat_ids:
        return False

    if config.allowed_user_ids is None:
        return True

    user_id = getattr(user, "id", None)
    return user_id is not None and int(user_id) in config.allowed_user_ids


def escape_markdown_v2(text: str) -> str:
    escaped = text
    for char in MARKDOWN_V2_SPECIAL_CHARS:
        escaped = escaped.replace(char, f"\\{char}")
    return escaped


def format_lift_payload(text: str) -> str:
    return escape_markdown_v2(text).replace("\n", "  \n")


def _display_participant(participant: str) -> str:
    if participant.startswith("id:"):
        return participant
    return f"@{participant}"


def _get_config(application: Application) -> BotConfig:
    config = application.bot_data.get(CONFIG_KEY)
    if not isinstance(config, BotConfig):
        raise RuntimeError("BotConfig not found in application.bot_data")
    return config


def _get_tracker(application: Application) -> GMTracker:
    tracker = application.bot_data.get(TRACKER_KEY)
    if not isinstance(tracker, GMTracker):
        raise RuntimeError("GMTracker not found in application.bot_data")
    return tracker


async def _guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    config = _get_config(context.application)
    if is_authorized_update(update, config):
        return True

    logger.warning(
        "Unauthorized request blocked. chat_id=%s user_id=%s",
        getattr(update.effective_chat, "id", None),
        getattr(update.effective_user, "id", None),
    )
    return False


async def send_gm(context: ContextTypes.DEFAULT_TYPE) -> None:
    config = _get_config(context.application)
    await context.bot.send_message(chat_id=config.chat_id, text="GM")
    await context.bot.send_animation(
        chat_id=config.chat_id,
        animation="https://media.tenor.com/y1n4lM9lR_kAAAAM/take-no.gif",
    )


async def reset_gm_users(context: ContextTypes.DEFAULT_TYPE) -> None:
    tracker = _get_tracker(context.application)
    tracker.reset_daily()
    logger.info("Daily GM state reset.")


async def check_all_gm_sent(context: ContextTypes.DEFAULT_TYPE) -> None:
    config = _get_config(context.application)
    tracker = _get_tracker(context.application)
    missing_users = tracker.get_missing_participants()

    if not missing_users:
        await context.bot.send_message(chat_id=config.chat_id, text="EUCH AUCH EINEN GUTEN MORGEN!")
        await context.bot.send_photo(
            chat_id=config.chat_id,
            photo="https://picr.eu/images/2023/04/18/FpnQl.jpg",
        )
        return

    missing_mentions = ", ".join(_display_participant(user) for user in missing_users)
    await context.bot.send_message(
        chat_id=config.chat_id,
        text=f"Fehlende GM-Nachrichten von: {missing_mentions}",
    )


async def send_poem(context: ContextTypes.DEFAULT_TYPE) -> None:
    config = _get_config(context.application)
    poem = "Stahl in den Handen,\nMuskeln wachsen, Kraft erwacht,\nKorper formen sich.\nGN."
    await context.bot.send_message(chat_id=config.chat_id, text=poem)
    await context.bot.send_photo(
        chat_id=config.chat_id,
        photo="https://picr.eu/images/2023/04/18/Fp87k.jpg",
    )


async def gm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return
    await send_gm(context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return
    chat = update.effective_chat
    if chat is None:
        return
    await context.bot.send_message(chat_id=chat.id, text="ham ham lecker eisen")


async def check_gm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return

    if update.message is None or update.message.text is None:
        return

    user = update.effective_user
    user_id = getattr(user, "id", None)
    username = getattr(user, "username", None)

    tracker = _get_tracker(context.application)
    tracker.record_activity(user_id=user_id, username=username)

    if update.message.text.strip().lower() == "gm":
        tracker.record_gm(user_id=user_id, username=username)
        logger.info("GM recorded for participant=%s", tracker.participant_key(user_id, username))


async def lift_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return

    if update.message is None or update.message.text is None:
        return

    config = _get_config(context.application)
    message_text = update.message.text.partition(" ")[2]
    if not message_text.strip():
        chat = update.effective_chat
        if chat is None:
            return
        await context.bot.send_message(
            chat_id=chat.id,
            text="Bitte geben Sie eine Nachricht nach dem /lift Befehl ein.",
        )
        return

    payload = format_lift_payload(message_text.strip())
    try:
        await context.bot.send_message(
            chat_id=config.chat_id,
            text=payload,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except BadRequest as exc:
        logger.warning("MarkdownV2 parsing failed. Falling back to plain text. error=%s", exc)
        await context.bot.send_message(chat_id=config.chat_id, text=message_text.strip())


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return

    config = _get_config(context.application)
    quote = (
        "I have found the Iron to be my greatest friend.\n"
        "It never freaks out on me, never runs.\n"
        "Friends may come and go.\n"
        "But two hundred pounds is always two hundred pounds."
    )
    await context.bot.send_message(chat_id=config.chat_id, text=quote)


async def nako_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update, context):
        return

    chat = update.effective_chat
    if chat is None:
        return

    message = (
        "Im Labyrinth der Seele wandert Michael,\n"
        "Verloren, suchend, wie ein Schatten blind,\n"
        "Zerfurcht sein Herz, sein Geist noch unbestandig,\n"
        "Ein junger Mann, der seinen Weg nicht findet.\n\n"
        "Der Lebenssturme wilder Tanz umhullt ihn,\n"
        "Zerrt ihn hinfort, verweht die Hoffnung fein,\n"
        "Die Qual der Wahl, die Schatten seiner Zweifel,\n"
        "Lahmen seinen Geist, gefangen im Sein.\n\n"
        "Und schliesslich kommt er an, am Rand der Welt,\n"
        "Ein kleines Land, von blauem Meer umspult,\n"
        "Er dachte, er fande hier das Paradies,\n"
        "Aber es war Malta, und Malta war ok."
    )
    await context.bot.send_message(chat_id=chat.id, text=message)


def _exception_info(
    error: BaseException,
) -> tuple[type[BaseException], BaseException, TracebackType | None]:
    return (type(error), error, error.__traceback__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE | object) -> None:
    del update
    error = getattr(context, "error", None)
    if error is None:
        logger.error("error_handler invoked without exception context.")
        return

    if isinstance(error, TelegramError):
        logger.error("Telegram API error: %s", error, exc_info=_exception_info(error))
        return

    if isinstance(error, BaseException):
        logger.error(
            "Unhandled non-telegram exception.",
            exc_info=_exception_info(error),
        )
        return

    logger.error("Unhandled error object: %r", error)


def build_application(config: BotConfig) -> Application:
    application = ApplicationBuilder().token(config.bot_token).build()
    application.bot_data[CONFIG_KEY] = config
    application.bot_data[TRACKER_KEY] = GMTracker(static_user_ids=config.allowed_user_ids)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("lift", lift_command))
    application.add_handler(CommandHandler("gm", gm_command))
    application.add_handler(CommandHandler("rollins", quote_command))
    application.add_handler(CommandHandler("nako", nako_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_gm))
    application.add_error_handler(error_handler)

    if application.job_queue is None:
        raise RuntimeError("JobQueue is not available. Install python-telegram-bot with job-queue extras.")

    timezone = ZoneInfo(config.timezone)
    application.job_queue.run_daily(send_gm, time=day_time(hour=5, tzinfo=timezone), name="send_gm")
    application.job_queue.run_daily(
        reset_gm_users,
        time=day_time(hour=0, tzinfo=timezone),
        name="reset_gm_users",
    )
    application.job_queue.run_daily(
        check_all_gm_sent,
        time=day_time(hour=9, tzinfo=timezone),
        name="check_all_gm_sent",
    )
    application.job_queue.run_daily(
        send_poem,
        time=day_time(hour=22, tzinfo=timezone),
        name="send_poem",
    )
    return application


def main() -> None:
    config = load_config_from_env()
    logger.info("Starting liftotron bot for chat_id=%s timezone=%s", config.chat_id, config.timezone)
    application = build_application(config)
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except ConfigError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
