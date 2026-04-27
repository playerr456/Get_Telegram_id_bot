# @see_tg_id_bot

Этот бот отправляет в ответ:
- Telegram ID пользователя, который написал боту
- исходный ID пересланного сообщения (если Telegram его предоставляет)
- кнопку `Copy ID` в один клик, если ID доступен

## Запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Убедитесь, что файл `bot_token.env` существует в корне проекта:
- токен в одной строке:
  - `123456:ABCDEF...`
- или в формате ключ/значение:
  - `BOT_TOKEN=123456:ABCDEF...`

3. Запустите бота:

```bash
python bot.py
```

## Развёртывание на Linux-сервере (через PuTTY)

1. Подключитесь к серверу через PuTTY (SSH), затем выполните:

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

2. Создайте файл с токеном:

```bash
cat > bot_token.env << 'EOF'
PASTE_YOUR_BOT_TOKEN_HERE
EOF
chmod 600 bot_token.env
```

3. Создайте сервис `systemd`:

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

4. Запустите сервис и включите автозапуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now get-tg-id-bot
sudo systemctl status get-tg-id-bot --no-pager
```

5. Просмотр логов:

```bash
journalctl -u get-tg-id-bot -f
```

## Обновление на сервере

```bash
cd ~/Get_tg_id_bot
git pull
. .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart get-tg-id-bot
```
