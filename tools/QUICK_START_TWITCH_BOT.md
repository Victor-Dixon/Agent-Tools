# 🚀 QUICK START: Twitch Bot Setup (RIGHT NOW)

## ⚡ Fast Setup (3 Steps)

### Step 1: Get OAuth Token (2 minutes)

1. Open: https://twitchapps.com/tmi/
2. Click "Connect with Twitch"
3. Authorize with your bot account (or your main account if you don't have a bot account)
4. Copy the OAuth token (starts with `oauth:`)

### Step 2: Create Config File (30 seconds)

Create file: `config/chat_presence.json`

```json
{
  "twitch": {
    "username": "YOUR_TWITCH_USERNAME",
    "oauth_token": "oauth:YOUR_TOKEN_HERE",
    "channel": "YOUR_CHANNEL_NAME"
  }
}
```

**Important:**
- `username`: Your Twitch username (lowercase, no spaces)
- `oauth_token`: The full token from step 1 (including `oauth:`)
- `channel`: Your channel name (lowercase, no `#` prefix)

### Step 3: Install Dependencies & Run (1 minute)

```bash
# Install dependencies (if not already installed)
pip install websockets irc

# Run the bot
python tools/chat_presence_cli.py --twitch-only
```

---

## 🎯 That's It!

The bot will:
- Connect to your Twitch channel
- Join chat automatically
- Respond to commands like `!agent7`, `!team`, etc.

---

## 💬 Test Commands

Try these in your chat:
- `!agent7 hello` - Agent-7 responds
- `!team status` - All agents respond
- `!swarm hello` - Broadcast message

---

## 🐛 Troubleshooting

**Bot not connecting?**
- Check OAuth token format (must start with `oauth:`)
- Verify channel name matches exactly (lowercase)
- Make sure bot account is not banned

**No responses?**
- Check console logs for errors
- Verify bot joined your channel (should see in chat)
- Try direct command: `!agent7 test`

---

**Need help? Check the full guide: `docs/chat_presence/CHAT_PRESENCE_SYSTEM.md`**



