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
- Set instance count to `1`

### Single Poller Rule
- Only one process may call `getUpdates` for your token.
- Do not run local `python bot.py` while Render worker is active.
- Do not run a second Render service with the same `BOT_TOKEN`.

If you need a public health URL, deploy `app.py` as a separate web service.

## 6. Initialize an Event
From Telegram (admin account):

```text
/new_event 1 | Grand Opening | 2026-03-30
```

## 7. Troubleshooting Polling Conflict
If logs show:

```text
telegram.error.Conflict: terminated by other getUpdates request
```

Apply this sequence:
1. Stop all duplicate bot processes (Render + local).
2. Confirm exactly one Render worker runs `python bot.py`.
3. Redeploy that single worker.
4. Rotate `BOT_TOKEN` in BotFather if token was exposed in logs/screenshots.
