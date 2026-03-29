from __future__ import annotations

from pathlib import Path
from typing import Tuple

from telegram import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    MessageOriginChannel,
    MessageOriginChat,
    MessageOriginHiddenUser,
    MessageOriginUser,
    Update,
)
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


def forwarded_source_info(message: Message) -> Tuple[str, str | None] | None:
    origin = message.forward_origin
    if origin is None:
        return None

    if isinstance(origin, MessageOriginUser):
        source_id = str(origin.sender_user.id)
        return f"Forwarded message author ID: {source_id}", source_id

    if isinstance(origin, MessageOriginChat):
        source_id = str(origin.sender_chat.id)
        return f"Forwarded message source ID (chat): {source_id}", source_id

    if isinstance(origin, MessageOriginChannel):
        source_id = str(origin.chat.id)
        return f"Forwarded message source ID (channel): {source_id}", source_id

    if isinstance(origin, MessageOriginHiddenUser):
        return "Forwarded message author ID is hidden by Telegram privacy settings.", None

    return "Could not determine forwarded message source.", None


def build_copy_id_markup(value: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Copy ID", copy_text=CopyTextButton(text=value))]]
    )


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

    forwarded_info = forwarded_source_info(message)
    reply_markup = None

    if forwarded_info is not None:
        forwarded_text, forwarded_id = forwarded_info
        lines = [forwarded_text]
        if forwarded_id:
            reply_markup = build_copy_id_markup(forwarded_id)
    else:
        user_id = str(user.id)
        lines = [f"Your Telegram ID: {user_id}"]
        reply_markup = build_copy_id_markup(user_id)

    await message.reply_text("\n".join(lines), reply_markup=reply_markup)


def main() -> None:
    token = load_bot_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, handle_message))

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
