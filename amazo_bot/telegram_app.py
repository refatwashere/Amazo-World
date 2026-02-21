from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from amazo_bot.config import load_settings
from amazo_bot.handlers.admin import AdminHandlers
from amazo_bot.handlers.user import TERMS, WALLET, UserHandlers
from amazo_bot.logging_config import configure_logging
from amazo_bot.services.giveaway_service import GiveawayService
from amazo_bot.services.supabase_service import SupabaseService


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    update_id = getattr(update, "update_id", "unknown")
    logging.exception("Unhandled exception for update_id=%s", update_id, exc_info=context.error)


def build_application() -> Application:
    configure_logging()
    settings = load_settings()

    supabase_service = SupabaseService(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key,
    )
    giveaway_service = GiveawayService(supabase_service)

    user_handlers = UserHandlers(supabase_service, giveaway_service)
    admin_handlers = AdminHandlers(settings.admin_id, supabase_service, giveaway_service)

    app = Application.builder().token(settings.bot_token).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("enter", user_handlers.enter_giveaway)],
        states={
            TERMS: [CallbackQueryHandler(user_handlers.terms_accepted, pattern="^accept_terms$")],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_handlers.save_wallet)],
        },
        fallbacks=[CommandHandler("cancel", user_handlers.cancel_entry)],
    )

    app.add_handler(CommandHandler("start", user_handlers.start))
    app.add_handler(conversation)
    app.add_handler(CommandHandler("balance", user_handlers.balance))
    app.add_handler(CommandHandler("leaderboard", user_handlers.leaderboard))
    app.add_handler(CommandHandler("history", user_handlers.history))
    app.add_handler(CommandHandler("help", user_handlers.faq_command))
    app.add_handler(CommandHandler("faq", user_handlers.faq_command))

    app.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    app.add_handler(CommandHandler("new_event", admin_handlers.new_event))
    app.add_handler(CommandHandler("pick", admin_handlers.pick_winners))
    app.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))

    app.add_handler(CallbackQueryHandler(user_handlers.enter_giveaway, pattern="^start_entry$"))
    app.add_handler(CallbackQueryHandler(user_handlers.faq_command, pattern="^show_faq$"))
    app.add_handler(CallbackQueryHandler(user_handlers.leaderboard, pattern="^show_lb$"))

    app.add_error_handler(on_error)
    return app

