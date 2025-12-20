# ⚡ Quick Setup: TWITCH_SWARM_VOICE in .env

## 📝 Add to your .env file:

```bash
# Format: username|oauth_token|channel (use | separator)
TWITCH_SWARM_VOICE=your_username|oauth:your_token_here|your_channel_name
```

### Example:
```bash
TWITCH_SWARM_VOICE=victor|oauth:abcdef123456789|yourchannelname
```

**Note:** Use `|` (pipe) as separator because OAuth tokens contain colons.

## 🚀 Then just run:

```bash
python tools/chat_presence_cli.py --twitch-only
```

That's it! The bot will connect automatically.

---

## 📋 Getting Your OAuth Token:

1. Go to: https://twitchapps.com/tmi/
2. Click "Connect with Twitch"
3. Authorize
4. Copy the token (it starts with `oauth:`)

---

## ✅ Format Notes:

- **Username**: Your Twitch username (lowercase, no spaces)
- **OAuth Token**: Full token including `oauth:` prefix
- **Channel**: Your channel name (lowercase, no `#` prefix)

The system will automatically parse it and connect!

