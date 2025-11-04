# 🚀 Telegram Auto-Forward Bot

A powerful Telegram bot that automatically forwards all incoming private messages to a backup group. Built with Pyrogram and designed for 24/7 operation on Railway.

## ✨ Features

- ✅ **Instant Forwarding** - Messages forwarded before they can be deleted
- ✅ **Clickable User Profiles** - Tap user names to open their profile
- ✅ **Detailed User Info** - Shows name, username, ID, verification status
- ✅ **Service Messages** - Forwards calls, voice chats, and other service messages
- ✅ **FloodWait Protection** - Auto-retries on Telegram rate limits
- ✅ **Flexible Group Setup** - Supports username, ID, or invite link
- ✅ **Production Ready** - Full error handling and logging
- ✅ **Zero Downtime** - Runs 24/7 on Railway

## 📋 Prerequisites

Before deploying, you need:

1. **Telegram API Credentials** (API_ID and API_HASH)
2. **Session String** (for bot authentication)
3. **Target Group** (where messages will be forwarded)
4. **GitHub Account** (for hosting code)
5. **Railway Account** (for deployment)

## 🔧 Setup Guide

### Step 1: Get API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### Step 2: Generate Session String

Run this script **locally** on your computer:

```python
from pyrogram import Client

api_id = input("Enter API_ID: ")
api_hash = input("Enter API_HASH: ")

with Client("my_account", api_id=int(api_id), api_hash=api_hash) as app:
    print("\n" + "="*60)
    print("YOUR SESSION STRING:")
    print("="*60)
    print(app.export_session_string())
    print("="*60)
```

**Requirements for local generation:**
```bash
pip install pyrogram tgcrypto
```

⚠️ **SECURITY WARNING**: Never share your session string! It gives full account access.

### Step 3: Prepare Your Target Group

**Option 1: Use Username (Recommended)**
1. Open your Telegram group
2. Go to: Group Info → Edit → Username
3. Set a username (max 32 characters, e.g., `mylogsbackup`)
4. Use: `@mylogsbackup` or just `mylogsbackup`

**Option 2: Use Group ID**
1. Forward any message from your group to @userinfobot
2. Copy the chat ID (e.g., `-1001234567890`)
3. Use that number directly

**Option 3: Use Invite Link**
1. Get group invite link: Group Info → Invite Link
2. Use the full link: `https://t.me/+xxxxxxxxxxxxx`

### Step 4: Deploy to Railway

#### 4.1 Fork/Upload to GitHub

1. Create a new repository on GitHub
2. Upload these files:
   - `main.py`
   - `requirements.txt`
   - `README.md` (this file)
   - `.gitignore` (optional)

#### 4.2 Connect to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

#### 4.3 Set Environment Variables

In Railway, go to your project → Variables tab → Add these:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Your Telegram API ID | `12345678` |
| `API_HASH` | Your Telegram API Hash | `abcdef123...` |
| `SESSION_STRING` | Generated session string | `BQC8sEg...` |
| `TARGET_GROUP` | Your backup group | `@logsbackup` |

#### 4.4 Deploy

Railway will automatically:
- Detect `requirements.txt`
- Install dependencies
- Start the bot

## 📊 Verification

Check Railway logs for:

```
✅ Client started
✅ Found group: YourGroupName (ID: -1001234567890)
✅ Startup notification sent
✅ BOT IS RUNNING!
```

You'll also see a startup message in your Telegram group!

## 📱 Message Format

When someone messages you, the bot forwards:

```
🔔 NEW MESSAGE RECEIVED
━━━━━━━━━━━━━━━━━━━━
👤 From: John Doe (clickable!)
🆔 User ID: 123456789
📝 Username: @johndoe
🔗 Profile: https://t.me/johndoe
✅ Verified Account
━━━━━━━━━━━━━━━━━━━━
[Original message forwarded below]
```

## 🔧 Troubleshooting

### "Username too long"
- Telegram usernames have a 32-character limit
- Shorten your group username in Telegram settings

### "Cannot access group"
- Verify your account is a member of the group
- For username: Ensure it's set in group settings
- Try using numeric ID instead

### "SESSION_STRING invalid"
- Regenerate the session string using the script above
- Ensure you copied the entire string (should be 200+ characters)

### "FloodWait" errors
- This is normal - Telegram rate limiting
- Bot automatically retries after waiting

### Bot stops after deployment
- Check Railway logs for error messages
- Verify all environment variables are set correctly
- Ensure session string is valid and not expired

## 📁 File Structure

```
telegram-forward-bot/
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore file (optional)
```

## 🔒 Security Best Practices

1. **Never commit sensitive data** to GitHub
   - Use Railway environment variables
   - Add `.env` to `.gitignore` if using locally

2. **Keep session string private**
   - Don't share in issues or PRs
   - Regenerate if compromised

3. **Rotate credentials regularly**
   - Generate new session strings periodically
   - Update API credentials if needed

4. **Monitor bot activity**
   - Check Railway logs regularly
   - Review forwarded messages

## 📄 .gitignore (Recommended)

Create a `.gitignore` file:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# Telegram session files
*.session
*.session-journal

# Environment files
.env
.env.local

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
```

## 🛠️ Local Development

To run locally for testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export SESSION_STRING="your_session_string"
export TARGET_GROUP="@yourgroup"

# Run bot
python main.py
```

## 📞 Support

If you encounter issues:

1. Check Railway logs for detailed error messages
2. Verify all environment variables are correct
3. Ensure session string is valid and not expired
4. Make sure you're a member of the target group
5. Check your internet connection and Telegram API status

## 📝 License

This project is open source and available for personal use.

## ⚠️ Disclaimer

- This bot uses your personal Telegram account
- The session string gives full account access
- Use responsibly and respect privacy laws
- Not affiliated with Telegram

## 🎯 Credits

Built with:
- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API framework
- [Railway](https://railway.app) - Deployment platform

---

**Made with ❤️ for message backup and logging**

**Star ⭐ this repo if you find it useful!**
