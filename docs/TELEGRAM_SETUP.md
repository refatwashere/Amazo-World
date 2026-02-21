# 📡 Telegram Infrastructure Setup

To build a professional community for **Amazo-World**, you must integrate three distinct components.

## 1. The Bot (@BotFather)
1. **Create:** Message `@BotFather` and use the `/newbot` command.
2. **Branding:** - `/setuserpic`: Upload the project logo.
   - `/setdescription`: Write a 1-sentence hook (e.g., "The ultimate referral-based giveaway engine.")
3. **Privacy:** Use `/setprivacy` and set it to **Disabled** if you want the bot to read messages in your group for future features.

## 2. The Announcement Channel
The Channel is for "Read-Only" official news.
1. Create a new Channel (Public or Private).
2. **Add Bot as Admin:** Give it the permission to `Post Messages`.
3. **Link to Bot:** Mention your bot's username in the Channel description.

## 3. The Community Group
The Group is where the "World" happens—chatting and engagement.
1. Create a new Group.
2. **Add Bot as Admin:** Ensure it can `Pin Messages` and `Delete Messages` (for future spam protection).
3. **Integration:** Link the Group to your Announcement Channel in the Group Settings so comments on posts show up in the chat.

## 4. Integration Logic
- **Member Check:** The bot uses the `get_chat_member` API method to verify if a user has joined the Channel/Group before allowing them to enter a giveaway. 
- **Broadcasts:** Use the `/broadcast` command to send updates to all users who have interacted with the bot, even if they aren't active in the group.