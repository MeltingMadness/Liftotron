# liftotron

Telegram bot runtime for daily GM workflows.

## Requirements

- Python 3.14+
- Telegram bot token from BotFather

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Configuration

Environment variables are mandatory. Copy `.env.example` as template and set real values in your local shell or secret manager.

```powershell
$env:BOT_TOKEN = "<new-rotated-token>"
$env:CHAT_ID = "-1001854584771"
$env:ALLOWED_CHAT_IDS = "-1001854584771"
$env:ALLOWED_USER_IDS = "123456789"
$env:TIMEZONE = "Europe/Berlin"
```

## Run

```powershell
python bot.py
```

If required configuration is missing, the process exits with a deterministic `Configuration error: ...` message.

## Quality Gate

```powershell
ruff check bot.py tests
mypy bot.py
python -m py_compile bot.py
pytest -q
bandit -r bot.py
pip-audit -r requirements.txt
```

## Security Notes

- Never commit `.env` or secrets.
- Rotate Telegram tokens immediately after exposure.
- Follow `docs/incident-response.md` for recovery and history cleanup.

