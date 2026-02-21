import os
import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from supabase import create_client, Client

# --- SETUP & CONFIGURATION ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Conversation States
TERMS = 0
WALLET = 1

# --- HELPER FUNCTIONS ---
async def get_active_event():
    """Fetches the current active giveaway and auto-closes if expired."""
    res = supabase.table("giveaways").select("*").eq("is_active", True).execute()
    if res.data:
        event = res.data[0]
        end_time = datetime.fromisoformat(event['end_date'].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) > end_time:
            supabase.table("giveaways").update({"is_active": False}).eq("id", event['id']).execute()
            return None
        return event
    return None

# --- USER COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initializes the bot with branding and captures referrals."""
    user = update.message.from_user
    
    # 1. Handle Referral Logic
    if context.args:
        # Don't let users refer themselves
        ref_id = int(context.args[0])
        if ref_id != user.id:
            context.user_data['referred_by'] = ref_id

    # 2. Branded Banner (Use a link to your hosted image)
    # If you don't have a link yet, you can send it as a local file.
    banner_url = "https://your-hosting.com/amazo_welcome_banner.jpg" 

    welcome_text = (
        f"👋 **Welcome to the Amazo-World, {user.first_name}!**\n\n"
        "You've entered the hub of referral-based giveaways. "
        "Our mission is to reward our most active community members with "
        "transparent, weighted draws.\n\n"
        "🚀 **Current Status:** Event #1 is LIVE!\n"
        "👥 **Your Power:** Every friend you invite = +1 Ticket."
    )

    # 3. Inline Buttons for a "Mini App" feel
    keyboard = [
        [InlineKeyboardButton("💎 Enter Giveaway", callback_data="start_entry")],
        [InlineKeyboardButton("📜 FAQ & Rules", callback_data="show_faq")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="show_lb")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Try sending with a photo
        await update.message.reply_photo(
            photo=banner_url,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except:
        # Fallback to text if image fails
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
async def enter_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the entry flow with T&C."""
    event = await get_active_event()
    if not event:
        await update.message.reply_text("🚫 No active giveaway at the moment. Stay tuned!")
        return ConversationHandler.END

    # Check if user already entered
    user_id = update.message.from_user.id
    check = supabase.table("entries").select("*").eq("user_id", user_id).eq("event_id", event['id']).execute()
    if check.data:
        await update.message.reply_text("✅ You are already registered for this event! Use /balance to check stats.")
        return ConversationHandler.END

    context.user_data['current_event_id'] = event['id']
    
    keyboard = [[InlineKeyboardButton("✅ I Accept", callback_data='accept_terms')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    terms_text = (
        f"📝 **Entering: {event['name']}**\n\n"
        "Before you proceed, please read and accept our community terms:\n"
        "1️⃣ No botting or multiple accounts.\n"
        "2️⃣ Double-check your wallet address; we cannot change it later.\n"
        "3️⃣ This is not financial advice.\n\n"
        "*Do you accept the terms?*"
    )
    await update.message.reply_text(terms_text, reply_markup=reply_markup, parse_mode='Markdown')
    return TERMS

async def terms_accepted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles T&C acceptance."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Terms Accepted! Now, please send your **Solana or Ethereum wallet address**:")
    return WALLET

async def save_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet = update.message.text.strip()
    
    # Basic validation: SOL addresses are ~44 chars, ETH are 42 chars starting with 0x
    if len(wallet) < 30 or len(wallet) > 50:
        await update.message.reply_text(
            "⚠️ That doesn't look like a valid SOL or ETH address.\n"
            "Please check your wallet address and send it again:"
        )
        return WALLET # Keeps them in the input state

    user = update.message.from_user
    event_id = context.user_data.get('current_event_id')
    referrer = context.user_data.get('referred_by')

    if referrer == user.id:
        referrer = None

    try:
        data = {
            "user_id": user.id,
            "event_id": event_id,
            "username": user.username or f"User_{user.id}",
            "wallet_address": wallet,
            "referred_by": referrer
        }
        supabase.table("entries").insert(data).execute()

        if referrer:
            supabase.rpc('increment_referral', {'row_id': referrer, 'target_event_id': event_id}).execute()

        ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user.id}"
        
        await update.message.reply_text(
            f"✅ Successfully registered for Event #{event_id}!\n\n"
            f"🔗 **Your Unique Referral Link:**\n`{ref_link}`\n\n"
            "_Note: You must join future events first before your link counts for them!_"
        )
    except Exception as e:
        # Supabase throws an error if they violate the unique constraint (already entered)
        await update.message.reply_text("Error saving data. You might already be registered for this event.")
        logging.error(f"Save error: {e}")

    return ConversationHandler.END

async def cancel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Registration cancelled.")
    return ConversationHandler.END

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows user stats for the active event."""
    user_id = update.message.from_user.id
    event = await get_active_event()

    if not event:
        await update.message.reply_text("No active event. Use /history to see past entries.")
        return

    res = supabase.table("entries").select("*").eq("user_id", user_id).eq("event_id", event['id']).execute()

    if res.data:
        data = res.data[0]
        ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"
        text = (
            f"🌟 **Current Event: {event['name']}**\n"
            f"💰 **Wallet:** `{data['wallet_address']}`\n"
            f"👥 **Referrals:** {data['referral_count']}\n"
            f"🎟️ **Total Tickets:** {data['referral_count'] + 1}\n\n"
            f"🔗 **Your Link:** {ref_link}"
        )
    else:
        text = f"You haven't joined **{event['name']}** yet! Use /enter."

    await update.message.reply_text(text, parse_mode='Markdown')

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows top referrers for the active event."""
    event = await get_active_event()
    if not event:
        await update.message.reply_text("No active event.")
        return

    res = supabase.table("entries") \
        .select("username, referral_count") \
        .eq("event_id", event['id']) \
        .order("referral_count", descending=True) \
        .limit(10).execute()

    if not res.data:
        await update.message.reply_text("Leaderboard is empty. Be the first to invite someone!")
        return

    text = f"🏆 **TOP REFERRERS: {event['name']}** 🏆\n\n"
    for i, user in enumerate(res.data, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        text += f"{medal} {i}. @{user['username']} — **{user['referral_count']}** referrals\n"

    await update.message.reply_text(text, parse_mode='Markdown')

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    res = supabase.table("entries").select("referral_count, giveaways(name, is_active)").eq("user_id", user_id).execute()

    if not res.data:
        await update.message.reply_text("You haven't participated in any events yet.")
        return

    text = "📜 **Your Amazo-World History**\n\n"
    for entry in res.data:
        event_name = entry['giveaways']['name']
        status = "🟢 Active" if entry['giveaways']['is_active'] else "🔴 Closed"
        text += f"🔹 **{event_name}** ({status})\n   Resulted in {entry['referral_count']} referrals\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ **Amazo-World FAQ**\n\n"
        "🔹 **How to enter?** Use /enter and follow the steps.\n"
        "🔹 **Referrals?** Get your link via /balance. 1 Friend = 1 Extra Ticket.\n"
        "🔹 **Winners?** Picked randomly per event. More tickets = higher chance.\n"
        "🔹 **Wallet?** We support SOL/ETH addresses.\n\n"
        "🛠 Need help? Contact an admin."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# --- ADMIN COMMANDS ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    event = await get_active_event()
    if not event:
        await update.message.reply_text("No active event. Launch one with /new_event.")
        return

    count_res = supabase.table("entries").select("user_id", count="exact").eq("event_id", event['id']).execute()
    ref_res = supabase.table("entries").select("referral_count").eq("event_id", event['id']).execute()
    
    total_users = count_res.count
    total_refs = sum(item['referral_count'] for item in ref_res.data)

    dashboard = (
        f"📊 **ADMIN DASHBOARD**\n"
        f"📌 **Current:** {event['name']} (ID: {event['id']})\n"
        f"👥 **Total Participants:** {total_users}\n"
        f"🔗 **Total Referrals:** {total_refs}\n"
        f"🎟️ **Total Tickets Issued:** {total_users + total_refs}"
    )
    await update.message.reply_text(dashboard, parse_mode='Markdown')

async def new_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    try:
        args = ' '.join(context.args).split('|')
        ev_id = int(args[0].strip())
        name = args[1].strip()
        date = args[2].strip() 
        
        supabase.table("giveaways").update({"is_active": False}).eq("is_active", True).execute()
        supabase.table("giveaways").insert({
            "id": ev_id, "name": name, "end_date": f"{date}T23:59:59Z", "is_active": True
        }).execute()

        await update.message.reply_text(f"✅ Event #{ev_id} '{name}' is LIVE until {date}!")
    except Exception as e:
        await update.message.reply_text("❌ Use format: `/new_event ID | Name | YYYY-MM-DD`")

async def pick_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Provide an Event ID. Example: `/pick 1`")
        return

    event_id = int(context.args[0])
    try:
        response = supabase.rpc("pick_winners_by_event", {"target_event_id": event_id}).execute()
        winners = response.data

        if not winners:
            await update.message.reply_text(f"No entries found for Event #{event_id}.")
            return

        text = f"🎊 **EVENT #{event_id} WINNERS** 🎊\n\n"
        for i, w in enumerate(winners, 1):
            text += f"{i}. @{w['username']} — `{w['wallet_address']}`\n"
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error drawing winners: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    msg = ' '.join(context.args)
    if not msg:
        await update.message.reply_text("Usage: `/broadcast [message]`")
        return

    res = supabase.table("entries").select("user_id").execute()
    users = {u['user_id'] for u in res.data} # Use set to avoid duplicates across multiple events
    
    count, failed = 0, 0
    await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **AMAZO-WORLD UPDATE**\n\n{msg}", parse_mode='Markdown')
            count += 1
        except:
            failed += 1

    await update.message.reply_text(f"✅ Broadcast Done!\n📤 Sent: {count}\n🚫 Failed: {failed}")

# --- MAIN EXECUTION ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('enter', enter_giveaway)],
        states={
            TERMS: [CallbackQueryHandler(terms_accepted, pattern='^accept_terms$')],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_wallet)]
        },
        fallbacks=[CommandHandler('cancel', cancel_entry)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("help", faq_command))
    app.add_handler(CommandHandler("faq", faq_command))
    
    # Admin commands
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("new_event", new_event))
    app.add_handler(CommandHandler("pick", pick_winners))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Inside your main() function, add these CallbackQueryHandlers
    app.add_handler(CallbackQueryHandler(enter_giveaway, pattern='^start_entry$'))
    app.add_handler(CallbackQueryHandler(faq_command, pattern='^show_faq$'))
    app.add_handler(CallbackQueryHandler(leaderboard, pattern='^show_lb$'))
    logging.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()