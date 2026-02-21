# 🚀 Installation & Deployment Guide

Follow these steps to deploy **Amazo-World** to Render.

## Step 1: GitHub Preparation
1. Create a new private repository.
2. Ensure your `requirements.txt` includes:
   - `python-telegram-bot`
   - `supabase`
   - `flask`
   - `gunicorn`
3. Push your code:
   
   ```bash
   git init
   git add .
   git commit -m "Genesis Launch"
   git push origin main
   
## Step 2: Render.com Setup
- Create a new Web Service.
- Connect your GitHub repository.
- Runtime: Python 3.10+
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app & python bot.py

## Step 3: Environment Variables (Secrets)
Go to the Environment tab in Render and add:

- BOT_TOKEN: From @BotFather.
- SUPABASE_URL: Your Project URL.
- SUPABASE_KEY: Your Anon Key.
- ADMIN_ID: Your numeric Telegram ID.

## Step 4: Keep-Alive (Cron-Job)
- Go to cron-job.org.
- Create a new job pointing to your Render URL (e.g., https://amazo-world.onrender.com/).
- Set the interval to 12 minutes.

## Step 5: Initialize the DB
- Open the bot on Telegram.
- Send /new_event 1 | Grand Opening | 2026-03-30.
- Your bot is now live and ready!