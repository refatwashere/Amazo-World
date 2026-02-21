import pytest

from amazo_bot.config import load_settings


def test_load_settings_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "key")
    monkeypatch.setenv("ADMIN_ID", "123")

    settings = load_settings()

    assert settings.bot_token == "token"
    assert settings.supabase_url == "https://example.supabase.co"
    assert settings.supabase_key == "key"
    assert settings.admin_id == 123


def test_load_settings_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "key")
    monkeypatch.setenv("ADMIN_ID", "123")

    with pytest.raises(ValueError, match="BOT_TOKEN"):
        load_settings()


def test_load_settings_invalid_admin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "key")
    monkeypatch.setenv("ADMIN_ID", "abc")

    with pytest.raises(ValueError, match="ADMIN_ID"):
        load_settings()

