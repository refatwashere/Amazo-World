# 🌐 Amazo-World: Telegram Giveaway & Referral System

**Amazo-World** is a professional-grade Telegram bot ecosystem designed to manage multi-event crypto giveaways. It features a weighted referral system, automated winner selection, and a complete admin suite.

---

## 🛠 Tech Stack
- **Backend:** Python 3.10+ (python-telegram-bot)
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Render (Free Tier)
- **Keep-Alive:** cron-job.org (12-minute intervals)

---

## 🗄️ Database Architecture (Supabase)

### 1. Tables
#### `giveaways`
- `id`: (Integer, Primary Key) Event Serial Number.
- `name`: (Text) Name of the giveaway event.
- `end_date`: (Timestamptz) Expiration date.
- `is_active`: (Boolean) Current status.

#### `entries`
- `user_id`: (BigInt) Telegram User ID.
- `event_id`: (Integer) Link to `giveaways.id`.
- `username`: (Text) Telegram handle.
- `wallet_address`: (Text) User's crypto address.
- `referral_count`: (Integer) Number of successful invites.
- `referred_by`: (BigInt) ID of the person who invited them.

### 2. Custom Functions (SQL)
- `increment_referral`: Safely updates counts for the inviter.
- `pick_winners_by_event`: Uses weighted randomness based on referrals to select 3 winners.

---

## 🚀 Deployment & Environment Variables

Add the following keys to your Render environment:

| Key | Description |
| :--- | :--- |
| `BOT_TOKEN` | API Token from @BotFather |
| `SUPABASE_URL` | Your Project URL |
| `SUPABASE_KEY` | Your Service Role/Anon Key |
| `ADMIN_ID` | Your numeric Telegram ID |

**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `gunicorn app:app & python bot.py`

---

## 🎮 Commands Reference

### 👤 User Commands
- `/start` - Launch the bot and view welcome branding.
- `/enter` - Read & Accept Terms, then register your wallet.
- `/balance` - Check current event referrals and get your unique link.
- `/leaderboard` - View top 10 referrers for the active event.
- `/history` - See past event participations.
- `/help` - View Frequently Asked Questions.

### ⚡ Admin Commands
- `/admin` - Dashboard showing total participants and referral stats.
- `/new_event [ID] | [Name] | [YYYY-MM-DD]` - Start a new giveaway cycle.
- `/pick [ID]` - Run the drawing to pick 3 winners for a specific event.
- `/broadcast [message]` - Send a formatted announcement to all users.

---

## 📜 Terms & Conditions (Default)
1. No multiple accounts or botting (Automatic disqualification).
2. Users must provide valid wallet addresses (Locked after submission).
3. Rewards are distributed within 48 hours of event closure.

---

## 📈 Maintenance
- **Rate Limiting:** If the community grows past 2,000 members, add a `time.sleep(0.05)` delay in the `/broadcast` loop to avoid Telegram's flood limits.
- **Database Activity:** Supabase stays active as long as the bot is pinged by `cron-job.org`.