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

If you need an HTTP health endpoint, deploy `app.py` as a separate web service.

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
