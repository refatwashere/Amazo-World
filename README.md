# Amazo-World

A Telegram giveaway and referral bot powered by Python and Supabase.

## Features
- Multi-event giveaway support
- Referral tracking with weighted winner selection
- User commands for entry, balance, leaderboard, and history
- Admin commands for event management, winner selection, and broadcast

## Tech Stack
- Python 3.10+
- `python-telegram-bot`
- Supabase (PostgreSQL + RPC)
- Optional Flask health endpoint (`app.py`)

## Project Structure
```text
Amazo-World/
  app.py
  bot.py
  amazo_bot/
    config.py
    logging_config.py
    telegram_app.py
    handlers/
    services/
  docs/
  tests/
```

## Environment Variables
Create `.env` with:

```env
BOT_TOKEN=
SUPABASE_URL=
SUPABASE_KEY=
ADMIN_ID=
```

## Local Run
Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Telegram worker:

```bash
python bot.py
```

Optional: run health endpoint:

```bash
python app.py
```

## Render Deployment (Recommended)
- Service type: Worker
- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Set environment variables in Render dashboard
- Scale worker count to exactly `1`

### Single Poller Rule (Critical)
- Never run `python bot.py` in more than one place using the same `BOT_TOKEN`.
- If Render worker is running, stop local bot sessions and any duplicate worker/web services that also start polling.

If you need an HTTP health endpoint, deploy `app.py` as a separate web service.

## Troubleshooting
### `409 Conflict` from `getUpdates`
- Symptom: `telegram.error.Conflict: terminated by other getUpdates request`
- Cause: multiple active pollers using the same bot token
- Resolution:
  1. Keep exactly one Render worker running `python bot.py`
  2. Stop any duplicate Render services or local bot process
  3. Redeploy the single worker
  4. If token was exposed, rotate in BotFather and update Render `BOT_TOKEN`

## Commands
User:
- `/start`
- `/enter`
- `/balance`
- `/leaderboard`
- `/history`
- `/help`
- `/faq`

Admin:
- `/admin`
- `/new_event ID | Name | YYYY-MM-DD`
- `/pick ID`
- `/broadcast message`
