# @see_tg_id_bot

This bot replies with:
- the Telegram ID of the user who wrote to the bot
- the source ID of a forwarded message (when Telegram provides it)
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

## Deploy On Linux Server (via PuTTY)

1. Connect to server with PuTTY (SSH), then run:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv
git clone https://github.com/playerr456/Get_tg_id_bot.git
cd Get_tg_id_bot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
deactivate
```

2. Create token file:

```bash
cat > bot_token.env << 'EOF'
PASTE_YOUR_BOT_TOKEN_HERE
EOF
chmod 600 bot_token.env
```

3. Create a systemd service:

```bash
APP_DIR="$HOME/Get_tg_id_bot"
SERVICE_USER="$(whoami)"
sudo tee /etc/systemd/system/get-tg-id-bot.service > /dev/null << EOF
[Unit]
Description=Get TG ID Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/bot.py
Restart=always
RestartSec=3
User=$SERVICE_USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
```

4. Start and enable autostart:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now get-tg-id-bot
sudo systemctl status get-tg-id-bot --no-pager
```

5. Logs:

```bash
journalctl -u get-tg-id-bot -f
```

## Update On Server

```bash
cd ~/Get_tg_id_bot
git pull
. .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart get-tg-id-bot
```
