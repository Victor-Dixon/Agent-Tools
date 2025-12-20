# 🎬 STREAM SETUP - RIGHT NOW

## ⚡ Add this to your `.env` file:

```bash
TWITCH_SWARM_VOICE=your_username|oauth:your_token_here|your_channel_name
```

**Example:**
```bash
TWITCH_SWARM_VOICE=victor|oauth:abcdef123456789|victorschannel
```

**Important:**
- Use `|` (pipe) as separator (not `:` because OAuth tokens have colons)
- OAuth token must include `oauth:` prefix
- All lowercase, no spaces

---

## 🚀 Then run:

```bash
python tools/chat_presence_cli.py --twitch-only
```

**That's it!** The bot will connect to your channel automatically.

---

## 🔑 Get OAuth Token (if you don't have it):

1. Go to: **https://twitchapps.com/tmi/**
2. Click "Connect with Twitch"
3. Authorize
4. Copy the full token (starts with `oauth:`)

---

## ✅ Test Commands in Chat:

Once connected, try:
- `!agent7 hello` - Agent-7 responds with personality 🌐⚡✨
- `!team status` - All agents respond
- `!swarm hello` - Broadcast message

---

## 🐛 Quick Fixes:

**Not connecting?**
- Check token format: must be `oauth:xxxxx`
- Channel name: lowercase, no `#`
- Make sure bot account isn't banned

**Need dependencies?**
```bash
pip install websockets irc python-dotenv
```

---

**The swarm is ready to join your stream!** 🚀



