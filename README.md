# TG ID Bot

This bot replies with:
- the Telegram ID of the user who wrote to the bot
- the source ID of a forwarded message (when Telegram provides it)
- ID for `@username` mentions when Bot API can resolve it
- a one-click `Copy ID` button when the ID is available

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure `bot_token.env` exists in project root:
- token as a single line:
  - `123456:ABCDEF...`
- or key/value format:
  - `BOT_TOKEN=123456:ABCDEF...`

3. Start the bot:

```bash
python bot.py
```
