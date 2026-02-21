# Telegram Setup

## 1. Create Bot with BotFather
1. Open `@BotFather`
2. Run `/newbot`
3. Save the generated token as `BOT_TOKEN`
4. Optional branding:
   - `/setuserpic`
   - `/setdescription`
   - `/setabouttext`

## 2. Admin Account
- Set your Telegram numeric user id as `ADMIN_ID`
- Admin-only commands are restricted by this id

## 3. Community Channels (Optional)
- Announcement channel for updates
- Discussion group for engagement
- Add the bot as admin only with permissions it needs

## 4. Deep-Link Referrals
- Referral links follow:
  `https://t.me/<bot_username>?start=<referrer_user_id>`
- The bot validates this payload and ignores malformed values.

## 5. Security Checklist
- Keep bot token private
- Never commit `.env`
- Rotate credentials immediately if exposed in logs or screenshots
