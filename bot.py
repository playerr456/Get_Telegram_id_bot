from __future__ import annotations

from pathlib import Path

from telegram import MessageOriginChannel, MessageOriginChat, MessageOriginHiddenUser, MessageOriginUser, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


def load_bot_token(env_path: str = "bot_token.env") -> str:
    token_file = Path(env_path)
    if not token_file.exists():
        raise FileNotFoundError(f"Token file not found: {token_file.resolve()}")

    for raw_line in token_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Support both formats: "TOKEN" and "BOT_TOKEN=TOKEN".
        value = line.split("=", maxsplit=1)[1].strip() if "=" in line else line
        value = value.strip("\"'")
        if value:
            return value

    raise ValueError("Could not read bot token from bot_token.env")


def forwarded_source_text(update: Update) -> str | None:
    message = update.effective_message
    if message is None:
        return None

    origin = message.forward_origin
    if origin is None:
        return None

    if isinstance(origin, MessageOriginUser):
        return f"Forwarded message author ID: {origin.sender_user.id}"

    if isinstance(origin, MessageOriginChat):
        return f"Forwarded message source ID (chat): {origin.sender_chat.id}"

    if isinstance(origin, MessageOriginChannel):
        return f"Forwarded message source ID (channel): {origin.chat.id}"

    if isinstance(origin, MessageOriginHiddenUser):
        return "Forwarded message author ID is hidden by Telegram privacy settings."

    return "Could not determine forwarded message source."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "Hi! Send me any message and I will show your Telegram ID.\n"
        "If the message is forwarded, I will try to show the source ID too."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    message = update.effective_message
    user = update.effective_user

    if message is None or user is None:
        return

    lines = [f"Your Telegram ID: {user.id}"]

    forwarded_line = forwarded_source_text(update)
    if forwarded_line:
        lines.append(forwarded_line)

    await message.reply_text("\n".join(lines))


def main() -> None:
    token = load_bot_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, handle_message))

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
