# liftotron Runbook

## Daily operation

- Process: `python bot.py`
- Required env vars: `BOT_TOKEN`, `CHAT_ID`, `ALLOWED_CHAT_IDS`
- Optional env vars: `ALLOWED_USER_IDS`, `TIMEZONE`

## Scheduled jobs (timezone from `TIMEZONE`)

- `05:00` send daily `GM` + animation
- `00:00` reset GM tracking state
- `09:00` check missing GM participants
- `22:00` send poem + image

## Monitoring and logs

- Logs are written to stdout.
- Check for these error classes:
  - `Telegram API error`
  - `Unhandled non-telegram exception`
  - `Unauthorized request blocked`

## Common failure cases

1. Missing env configuration:
   - Symptom: startup exits with `Configuration error`
   - Action: set required env vars and restart process.
2. Telegram parse errors in `/lift`:
   - Symptom: Markdown send fails
   - Action: fallback to plain text is automatic; verify escaping in tests.
3. Unauthorized command usage:
   - Symptom: command ignored and warning logged
   - Action: validate `ALLOWED_CHAT_IDS` and `ALLOWED_USER_IDS`.

## Recovery checklist

1. Rotate token if compromise is suspected.
2. Update secret store and runtime environment.
3. Restart bot process.
4. Run quality gate commands from `README.md`.
5. Re-run secret scans before merge/release.

