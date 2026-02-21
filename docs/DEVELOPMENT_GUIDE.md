# Development Guide

This guide explains the internal architecture and key flows.

## Architecture
- `bot.py`: minimal process entrypoint
- `amazo_bot/config.py`: environment loading and validation
- `amazo_bot/telegram_app.py`: app wiring and handler registration
- `amazo_bot/handlers/`: user and admin command handlers
- `amazo_bot/services/`: Supabase access and giveaway domain logic

## Core Flow: Referral Registration
1. User opens bot via referral deep-link (`/start <user_id>`).
2. Referral id is validated and saved in user context.
3. User runs `/enter` and accepts terms.
4. User submits wallet.
5. Entry is inserted into `entries`.
6. Referrer count is incremented through Supabase RPC.

## Event Lifecycle
- Active event is fetched from `giveaways`.
- Expired active events are automatically closed by comparing `end_date` with current UTC time.
- New events are created via `/new_event`.

## Reliability Rules
- Do not assume `update.message` exists; callback updates use `update.callback_query`.
- Use common reply helpers for safe response handling.
- Avoid leaking raw backend exceptions to users.
- Keep structured logs for operational debugging.

## Deployment Notes
- Default runtime is a single Telegram worker (`python bot.py`).
- `app.py` is optional and should be deployed separately only when an HTTP health endpoint is required.
