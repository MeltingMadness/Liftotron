from types import SimpleNamespace

from bot import BotConfig, is_authorized_update


def make_update(chat_id: int, user_id: int):
    return SimpleNamespace(
        effective_chat=SimpleNamespace(id=chat_id),
        effective_user=SimpleNamespace(id=user_id),
    )


def test_authorized_chat_and_user_is_allowed():
    config = BotConfig(
        bot_token="dummy",
        chat_id=-1001,
        allowed_chat_ids={-1001},
        allowed_user_ids={11, 22},
        timezone="Europe/Berlin",
    )
    update = make_update(-1001, 11)

    assert is_authorized_update(update, config) is True


def test_unauthorized_chat_is_blocked():
    config = BotConfig(
        bot_token="dummy",
        chat_id=-1001,
        allowed_chat_ids={-1001},
        allowed_user_ids=None,
        timezone="Europe/Berlin",
    )
    update = make_update(-9999, 11)

    assert is_authorized_update(update, config) is False


def test_unauthorized_user_is_blocked_when_user_allowlist_is_set():
    config = BotConfig(
        bot_token="dummy",
        chat_id=-1001,
        allowed_chat_ids={-1001},
        allowed_user_ids={11, 22},
        timezone="Europe/Berlin",
    )
    update = make_update(-1001, 999)

    assert is_authorized_update(update, config) is False

