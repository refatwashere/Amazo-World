# 💻 Web & Bot Development Guide

This document explains the logic behind the **Amazo-World** backend and how it interacts with Supabase.

## 1. The "Web" Component (Flask)
Since Render requires a web port to stay active, we use a simple Flask server inside `app.py`:
- **Keep-Alive:** The `health_check` route is pinged by `cron-job.org`.
- **Concurrency:** We run the Flask server and the Telegram Bot simultaneously using a multi-threaded or sub-process approach.

## 2. Referral Engine (Deep Linking)
The system uses Telegram's `start` parameter:
- **Link Format:** `https://t.me/YourBot?start=USER_ID`
- **Logic:** 1. User B clicks User A's link.
  2. Bot extracts `USER_ID` from the arguments.
  3. When User B submits a wallet, the bot triggers the `increment_referral` RPC in Supabase for User A.

## 3. Database Functions (Supabase SQL)
We use **Stored Procedures (RPC)** to ensure data integrity during high-traffic events.

### Weighted Randomness (Winner Selection)
The winner selection isn't just a random list; it’s "weighted." 
- **Calculation:** `Tickets = 1 (base) + Referral Count`.
- **SQL Logic:**
```sql
SELECT username, wallet_address 
FROM entries 
WHERE event_id = target_id 
ORDER BY (referral_count + 1) * random() DESC 
LIMIT 3;
```

## 4. State Management
The registration flow uses a ConversationHandler:

- **State 0 (TERMS):** Validates the user's agreement.

- **State 1 (WALLET):** Captures and validates the crypto address format.
