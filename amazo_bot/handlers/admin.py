from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from amazo_bot.handlers.common import reply_text_safe
from amazo_bot.services.giveaway_service import GiveawayService
from amazo_bot.services.supabase_service import SupabaseService


class AdminHandlers:
    def __init__(
        self,
        admin_id: int,
        supabase_service: SupabaseService,
        giveaway_service: GiveawayService,
    ) -> None:
        self.admin_id = admin_id
        self.supabase_service = supabase_service
        self.giveaway_service = giveaway_service

    def _is_admin(self, update: Update) -> bool:
        if not update.message:
            return False
        return update.message.from_user.id == self.admin_id

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_admin(update):
            return

        event = self.giveaway_service.get_active_event()
        if not event:
            await reply_text_safe(update, "No active event. Launch one with /new_event.")
            return

        event_id = int(event["id"])
        total_users = self.supabase_service.get_event_participant_count(event_id=event_id)
        total_refs = self.supabase_service.get_event_referral_total(event_id=event_id)

        text = (
            "ADMIN DASHBOARD\n"
            f"Current: {event['name']} (ID: {event_id})\n"
            f"Participants: {total_users}\n"
            f"Referrals: {total_refs}\n"
            f"Total tickets: {total_users + total_refs}"
        )
        await reply_text_safe(update, text)

    async def new_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_admin(update):
            return

        try:
            args = " ".join(context.args).split("|")
            event_id = int(args[0].strip())
            name = args[1].strip()
            date_yyyy_mm_dd = args[2].strip()

            self.supabase_service.deactivate_all_events()
            self.supabase_service.new_event(event_id, name, date_yyyy_mm_dd)
            await reply_text_safe(update, f"Event #{event_id} '{name}' is live until {date_yyyy_mm_dd}.")
        except (IndexError, ValueError):
            await reply_text_safe(update, "Use format: /new_event ID | Name | YYYY-MM-DD")
        except Exception:
            logging.exception("Failed to create new event")
            await reply_text_safe(update, "Could not create event right now. Try again.")

    async def pick_winners(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_admin(update):
            return
        if not context.args:
            await reply_text_safe(update, "Provide an event ID. Example: /pick 1")
            return

        try:
            event_id = int(context.args[0])
        except ValueError:
            await reply_text_safe(update, "Event ID must be an integer.")
            return

        try:
            winners = self.supabase_service.pick_winners(target_event_id=event_id)
            if not winners:
                await reply_text_safe(update, f"No entries found for Event #{event_id}.")
                return

            lines = [f"Event #{event_id} winners", ""]
            for i, winner in enumerate(winners, start=1):
                lines.append(
                    f"{i}. @{winner.get('username', 'unknown')} - {winner.get('wallet_address', 'n/a')}"
                )
            await reply_text_safe(update, "\n".join(lines))
        except Exception:
            logging.exception("Failed to pick winners for event_id=%s", event_id)
            await reply_text_safe(update, "Could not draw winners right now. Try again.")

    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_admin(update):
            return

        message = " ".join(context.args).strip()
        if not message:
            await reply_text_safe(update, "Usage: /broadcast [message]")
            return

        users = self.supabase_service.get_all_user_ids()
        await reply_text_safe(update, f"Broadcasting to {len(users)} users...")

        sent = 0
        failed = 0
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"AMAZO-WORLD UPDATE\n\n{message}",
                )
                sent += 1
            except Exception:
                failed += 1
                logging.exception("Broadcast failed for user_id=%s", user_id)

        await reply_text_safe(update, f"Broadcast done.\nSent: {sent}\nFailed: {failed}")

