import asyncio
import logging
from types import SimpleNamespace

from telegram.error import TelegramError

from bot import error_handler


def test_error_handler_with_none_error_logs_and_returns(caplog):
    context = SimpleNamespace(error=None)

    with caplog.at_level(logging.ERROR):
        asyncio.run(error_handler(update=None, context=context))

    assert "without exception context" in caplog.text


def test_error_handler_with_telegram_error_logs_specific_message(caplog):
    context = SimpleNamespace(error=TelegramError("telegram boom"))

    with caplog.at_level(logging.ERROR):
        asyncio.run(error_handler(update=None, context=context))

    assert "Telegram API error" in caplog.text


def test_error_handler_with_generic_error_logs_stacktrace_message(caplog):
    context = SimpleNamespace(error=RuntimeError("generic boom"))

    with caplog.at_level(logging.ERROR):
        asyncio.run(error_handler(update=None, context=context))

    assert "Unhandled non-telegram exception" in caplog.text

