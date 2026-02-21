from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from amazo_bot.services.supabase_service import SupabaseService


class GiveawayService:
    def __init__(self, supabase_service: SupabaseService) -> None:
        self.supabase_service = supabase_service

    def get_active_event(self) -> dict[str, Any] | None:
        event = self.supabase_service.fetch_active_event_record()
        if not event:
            return None

        end_time = datetime.fromisoformat(event["end_date"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > end_time:
            self.supabase_service.set_event_active_state(int(event["id"]), False)
            return None
        return event

