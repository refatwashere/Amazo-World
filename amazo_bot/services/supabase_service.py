from __future__ import annotations

from typing import Any

from supabase import Client, create_client


class SupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str) -> None:
        self.client: Client = create_client(supabase_url, supabase_key)

    def fetch_active_event_record(self) -> dict[str, Any] | None:
        res = self.client.table("giveaways").select("*").eq("is_active", True).execute()
        if not res.data:
            return None
        return res.data[0]

    def set_event_active_state(self, event_id: int, is_active: bool) -> None:
        self.client.table("giveaways").update({"is_active": is_active}).eq("id", event_id).execute()

    def get_active_event(self) -> dict[str, Any] | None:
        return self.fetch_active_event_record()

    def register_entry(
        self,
        user_id: int,
        event_id: int,
        username: str,
        wallet_address: str,
        referred_by: int | None,
    ) -> None:
        payload = {
            "user_id": user_id,
            "event_id": event_id,
            "username": username,
            "wallet_address": wallet_address,
            "referred_by": referred_by,
        }
        self.client.table("entries").insert(payload).execute()

    def increment_referral(self, referrer_id: int, target_event_id: int) -> None:
        self.client.rpc(
            "increment_referral",
            {"row_id": referrer_id, "target_event_id": target_event_id},
        ).execute()

    def get_user_entry_for_event(self, user_id: int, event_id: int) -> dict[str, Any] | None:
        res = (
            self.client.table("entries")
            .select("*")
            .eq("user_id", user_id)
            .eq("event_id", event_id)
            .execute()
        )
        if not res.data:
            return None
        return res.data[0]

    def get_leaderboard(self, event_id: int, limit: int = 10) -> list[dict[str, Any]]:
        res = (
            self.client.table("entries")
            .select("username, referral_count")
            .eq("event_id", event_id)
            .order("referral_count", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []

    def get_user_history(self, user_id: int) -> list[dict[str, Any]]:
        res = (
            self.client.table("entries")
            .select("referral_count, giveaways(name, is_active)")
            .eq("user_id", user_id)
            .execute()
        )
        return res.data or []

    def get_event_participant_count(self, event_id: int) -> int:
        res = (
            self.client.table("entries")
            .select("user_id", count="exact")
            .eq("event_id", event_id)
            .execute()
        )
        return int(res.count or 0)

    def get_event_referral_total(self, event_id: int) -> int:
        res = self.client.table("entries").select("referral_count").eq("event_id", event_id).execute()
        return sum(item.get("referral_count", 0) for item in (res.data or []))

    def deactivate_all_events(self) -> None:
        self.client.table("giveaways").update({"is_active": False}).eq("is_active", True).execute()

    def new_event(self, event_id: int, name: str, date_yyyy_mm_dd: str) -> None:
        self.client.table("giveaways").insert(
            {
                "id": event_id,
                "name": name,
                "end_date": f"{date_yyyy_mm_dd}T23:59:59Z",
                "is_active": True,
            }
        ).execute()

    def pick_winners(self, target_event_id: int) -> list[dict[str, Any]]:
        res = self.client.rpc("pick_winners_by_event", {"target_event_id": target_event_id}).execute()
        return res.data or []

    def get_all_user_ids(self) -> set[int]:
        res = self.client.table("entries").select("user_id").execute()
        return {int(row["user_id"]) for row in (res.data or [])}

