import pytest

from bot import ConfigError, load_config_from_env


def test_load_config_missing_bot_token_raises():
    env = {
        "CHAT_ID": "-100123",
        "ALLOWED_CHAT_IDS": "-100123",
    }

    with pytest.raises(ConfigError):
        load_config_from_env(env)


def test_load_config_parses_required_and_optional_fields():
    env = {
        "BOT_TOKEN": "dummy-token",
        "CHAT_ID": "-1001854584771",
        "ALLOWED_CHAT_IDS": "-1001854584771,-10042",
        "ALLOWED_USER_IDS": "1,2,3",
        "TIMEZONE": "Europe/Berlin",
    }

    config = load_config_from_env(env)

    assert config.bot_token == "dummy-token"
    assert config.chat_id == -1001854584771
    assert config.allowed_chat_ids == {-1001854584771, -10042}
    assert config.allowed_user_ids == {1, 2, 3}
    assert config.timezone == "Europe/Berlin"
