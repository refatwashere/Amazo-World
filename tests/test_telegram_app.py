from telegram.ext import CommandHandler, ConversationHandler

from amazo_bot.config import Settings
from amazo_bot.telegram_app import build_application


class DummySupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str) -> None:
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key

    def fetch_active_event_record(self):
        return None

    def set_event_active_state(self, event_id: int, is_active: bool) -> None:
        return None


def test_build_application_registers_expected_command_handlers(monkeypatch) -> None:
    monkeypatch.setattr(
        "amazo_bot.telegram_app.load_settings",
        lambda: Settings(
            bot_token="123:TESTTOKEN",
            supabase_url="https://example.supabase.co",
            supabase_key="key",
            admin_id=1,
        ),
    )
    monkeypatch.setattr("amazo_bot.telegram_app.SupabaseService", DummySupabaseService)

    app = build_application()

    commands = set()
    enter_registered = False
    for handlers in app.handlers.values():
        for handler in handlers:
            if isinstance(handler, CommandHandler):
                commands.update(handler.commands)
            if isinstance(handler, ConversationHandler):
                for entry in handler.entry_points:
                    if isinstance(entry, CommandHandler) and "enter" in entry.commands:
                        enter_registered = True

    assert {"start", "balance", "leaderboard", "history", "help", "faq"}.issubset(commands)
    assert {"admin", "new_event", "pick", "broadcast"}.issubset(commands)
    assert enter_registered is True
