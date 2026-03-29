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
from telegram.constants import MessageEntityType
from telegram.error import BadRequest
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


async def mentioned_target_info(
    message: Message, context: ContextTypes.DEFAULT_TYPE
) -> Tuple[str, str | None] | None:
    text_entities = message.parse_entities(
        types=[MessageEntityType.TEXT_MENTION, MessageEntityType.MENTION]
    )
    caption_entities = message.parse_caption_entities(
        types=[MessageEntityType.TEXT_MENTION, MessageEntityType.MENTION]
    )

    merged_entities = {**text_entities, **caption_entities}
    if not merged_entities:
        return None

    # text_mention contains a direct user object with ID.
    for entity, parsed_value in merged_entities.items():
        if entity.type != MessageEntityType.TEXT_MENTION or entity.user is None:
            continue

        target_id = str(entity.user.id)
        display = parsed_value or entity.user.full_name
        return f"Mentioned user ID ({display}): {target_id}", target_id

    # For plain @username mentions, try to resolve via Bot API get_chat.
    for entity, parsed_value in merged_entities.items():
        if entity.type != MessageEntityType.MENTION:
            continue

        if not parsed_value.startswith("@"):
            continue

        username = parsed_value
        try:
            target_chat = await context.bot.get_chat(username)
        except BadRequest:
            return (
                f"Could not resolve {username} to an ID. "
                "Telegram Bot API often hides user IDs for @username mentions.",
                None,
            )

        target_id = str(target_chat.id)
        if target_chat.type == "private":
            return f"Mentioned user ID ({username}): {target_id}", target_id
        return f"Mentioned chat ID ({username}): {target_id}", target_id

    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "Hi! Send me any message and I will show your Telegram ID.\n"
        "If the message is forwarded, I will try to show the source ID too.\n"
        "If you send @username, I will try to resolve and show that ID."
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
        mentioned_info = await mentioned_target_info(message, context)
        if mentioned_info is not None:
            mentioned_text, mentioned_id = mentioned_info
            lines = [mentioned_text]
            if mentioned_id:
                reply_markup = build_copy_id_markup(mentioned_id)
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
