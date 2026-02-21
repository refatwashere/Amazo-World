from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from amazo_bot.handlers.common import escape_markdown_text, parse_referral_arg, reply_text_safe
from amazo_bot.services.giveaway_service import GiveawayService
from amazo_bot.services.supabase_service import SupabaseService

TERMS = 0
WALLET = 1


class UserHandlers:
    def __init__(self, supabase_service: SupabaseService, giveaway_service: GiveawayService) -> None:
        self.supabase_service = supabase_service
        self.giveaway_service = giveaway_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return

        user = update.message.from_user
        referral_id = parse_referral_arg(context.args)
        if referral_id and referral_id != user.id:
            context.user_data["referred_by"] = referral_id

        welcome_text = (
            f"Welcome to Amazo-World, {escape_markdown_text(user.first_name)}\\!\n\n"
            "Referral based giveaways with transparent winner selection\\.\n"
            "Use the buttons below to begin\\."
        )

        keyboard = [
            [InlineKeyboardButton("Enter Giveaway", callback_data="start_entry")],
            [InlineKeyboardButton("FAQ and Rules", callback_data="show_faq")],
            [InlineKeyboardButton("Leaderboard", callback_data="show_lb")],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        await reply_text_safe(
            update,
            welcome_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )

    async def enter_giveaway(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        event = self.giveaway_service.get_active_event()
        if not event:
            await reply_text_safe(update, "No active giveaway at the moment.")
            return ConversationHandler.END

        context.user_data["current_event_id"] = int(event["id"])

        keyboard = [[InlineKeyboardButton("I Accept", callback_data="accept_terms")]]
        markup = InlineKeyboardMarkup(keyboard)
        event_name = str(event["name"])
        terms_text = (
            f"Entering: {event_name}\n\n"
            "Please read and accept the terms:\n"
            "1) No botting or multiple accounts.\n"
            "2) Wallet address cannot be changed later.\n"
            "3) This is not financial advice.\n\n"
            "Do you accept the terms?"
        )

        await reply_text_safe(update, terms_text, reply_markup=markup)
        return TERMS

    async def terms_accepted(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        if not update.callback_query:
            return ConversationHandler.END
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Terms accepted. Send your Solana or Ethereum wallet address:"
        )
        return WALLET

    async def save_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message:
            return ConversationHandler.END

        wallet = update.message.text.strip()
        if len(wallet) < 30 or len(wallet) > 50:
            await reply_text_safe(
                update,
                "That does not look like a valid SOL or ETH address. Please try again:",
            )
            return WALLET

        user = update.message.from_user
        event_id = int(context.user_data.get("current_event_id", 0))
        referrer = context.user_data.get("referred_by")
        if referrer == user.id:
            referrer = None

        try:
            self.supabase_service.register_entry(
                user_id=user.id,
                event_id=event_id,
                username=user.username or f"User_{user.id}",
                wallet_address=wallet,
                referred_by=referrer,
            )
            if referrer:
                self.supabase_service.increment_referral(
                    referrer_id=int(referrer),
                    target_event_id=event_id,
                )

            bot_name = (await context.bot.get_me()).username
            ref_link = f"https://t.me/{bot_name}?start={user.id}"
            text = (
                f"Successfully registered for Event #{event_id}.\n\n"
                f"Your referral link:\n{ref_link}"
            )
            await reply_text_safe(update, text)
        except Exception:
            logging.exception("Failed to register wallet for user_id=%s event_id=%s", user.id, event_id)
            await reply_text_safe(
                update,
                "Could not save your registration right now. Please try again in a minute.",
            )

        return ConversationHandler.END

    async def cancel_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await reply_text_safe(update, "Registration cancelled.")
        return ConversationHandler.END

    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        user_id = update.message.from_user.id
        event = self.giveaway_service.get_active_event()
        if not event:
            await reply_text_safe(update, "No active event. Use /history to see previous entries.")
            return

        entry = self.supabase_service.get_user_entry_for_event(user_id=user_id, event_id=int(event["id"]))
        if not entry:
            await reply_text_safe(update, f"You have not joined {event['name']} yet. Use /enter.")
            return

        bot_name = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_name}?start={user_id}"
        referrals = int(entry.get("referral_count", 0))
        text = (
            f"Current event: {event['name']}\n"
            f"Wallet: {entry['wallet_address']}\n"
            f"Referrals: {referrals}\n"
            f"Total tickets: {referrals + 1}\n\n"
            f"Your link: {ref_link}"
        )
        await reply_text_safe(update, text)

    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        event = self.giveaway_service.get_active_event()
        if not event:
            await reply_text_safe(update, "No active event.")
            return

        leaderboard = self.supabase_service.get_leaderboard(event_id=int(event["id"]), limit=10)
        if not leaderboard:
            await reply_text_safe(update, "Leaderboard is empty. Be the first to invite someone.")
            return

        lines = [f"Top referrers: {event['name']}", ""]
        for index, row in enumerate(leaderboard, start=1):
            username = row.get("username") or "unknown_user"
            refs = int(row.get("referral_count", 0))
            lines.append(f"{index}. @{username} - {refs} referrals")
        await reply_text_safe(update, "\n".join(lines))

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        user_id = update.message.from_user.id
        rows = self.supabase_service.get_user_history(user_id=user_id)
        if not rows:
            await reply_text_safe(update, "You have not participated in any events yet.")
            return

        lines = ["Your Amazo-World history", ""]
        for row in rows:
            giveaway = row.get("giveaways") or {}
            name = giveaway.get("name", "Unknown")
            status = "Active" if giveaway.get("is_active") else "Closed"
            lines.append(f"- {name} ({status}): {row.get('referral_count', 0)} referrals")
        await reply_text_safe(update, "\n".join(lines))

    async def faq_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (
            "Amazo-World FAQ\n\n"
            "How to enter: Use /enter and follow the steps.\n"
            "Referrals: Get your link with /balance.\n"
            "Winners: Drawn per event using weighted tickets.\n"
            "Wallets: SOL and ETH format accepted.\n\n"
            "Need help? Contact an admin."
        )
        await reply_text_safe(update, text)

