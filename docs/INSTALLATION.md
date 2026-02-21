# Installation and Deployment Guide

## 1. Prerequisites
- Python 3.10 or newer
- Supabase project with required tables/RPCs
- Telegram bot token from `@BotFather`

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure Environment
Create `.env` (or set platform environment variables):

```env
BOT_TOKEN=
SUPABASE_URL=
SUPABASE_KEY=
ADMIN_ID=
```

## 4. Run Locally
Run the Telegram worker:

```bash
python bot.py
```

Optional health endpoint:

```bash
python app.py
```

## 5. Deploy to Render (Worker)
- Create a new Worker service
- Connect repository
- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Add required environment variables

If you need a public health URL, deploy `app.py` as a separate web service.

## 6. Initialize an Event
From Telegram (admin account):

```text
/new_event 1 | Grand Opening | 2026-03-30
```
