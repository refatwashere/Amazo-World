from __future__ import annotations

from typing import Any

from telegram import Message, Update
from telegram.error import TelegramError
from telegram.helpers import escape_markdown


def get_reply_message(update: Update) -> Message | None:
    if update.message:
        return update.message
    if update.callback_query and update.callback_query.message:
        return update.callback_query.message
    return None


def parse_referral_arg(args: list[str]) -> int | None:
    if not args:
        return None
    try:
        referral_id = int(args[0])
    except (ValueError, TypeError):
        return None
    return referral_id if referral_id > 0 else None


def escape_markdown_text(text: str) -> str:
    return escape_markdown(text, version=2)


async def reply_text_safe(
    update: Update,
    text: str,
    *,
    parse_mode: str | None = None,
    reply_markup: Any | None = None,
) -> bool:
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except TelegramError:
            pass

    message = get_reply_message(update)
    if not message:
        return False

    kwargs: dict[str, Any] = {}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    await message.reply_text(text, **kwargs)
    return True
