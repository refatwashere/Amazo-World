import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    supabase_url: str
    supabase_key: str
    admin_id: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    bot_token = _require_env("BOT_TOKEN")
    supabase_url = _require_env("SUPABASE_URL")
    supabase_key = _require_env("SUPABASE_KEY")
    admin_raw = _require_env("ADMIN_ID")

    try:
        admin_id = int(admin_raw)
    except ValueError as exc:
        raise ValueError("ADMIN_ID must be a valid integer.") from exc

    if admin_id <= 0:
        raise ValueError("ADMIN_ID must be a positive integer.")

    return Settings(
        bot_token=bot_token,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        admin_id=admin_id,
    )

