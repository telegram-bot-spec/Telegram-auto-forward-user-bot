# 🚀 Telegram Auto-Forward Bot

**Instantly forwards ALL incoming private messages to your backup group!**

## 🎯 What it does

✅ **Forwards EVERY private message** you receive to a backup group  
✅ **INSTANT forwarding** - catches messages before they're deleted  
✅ **Includes sender info** - name, username, user ID, profile link  
✅ **Only NEW messages** - doesn't touch old/existing messages  
✅ **Only PRIVATE chats** - ignores groups and channels  
✅ **Always online** - runs 24/7 on Railway for FREE  

## ⚠️ IMPORTANT SECURITY

**NEVER share or commit:**
- `API_ID` - Your Telegram API ID
- `API_HASH` - Your Telegram API Hash  
- `SESSION_STRING` - Your account session (like a password!)
- `TARGET_GROUP` - Your backup group link

## 📋 Setup Guide

### Step 1: Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Login with your phone number
3. Click "API Development Tools"
4. Create an app
5. Copy your `API_ID` and `API_HASH`

### Step 2: Generate Session String

Create `generate_session.py`:

```python
from pyrogram import Client

API_ID = input("Enter API_ID: ")
API_HASH = input("Enter API_HASH: ")

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

with app:
    print("\n✅ Your SESSION_STRING:\n")
    print(app.export_session_string())
    print("\n⚠️ Keep this SECRET! Never share it!")
```

Run it locally:
```bash
pip install pyrogram tgcrypto
python generate_session.py
```

**Save the SESSION_STRING securely!**

### Step 3: Create Your Backup Group

1. Open Telegram
2. Create a **private group** (just you, or with trusted people)
3. Get the invite link: Group Settings → Invite Link
4. Copy the link (looks like: `https://t.me/+ABC123xyz`)

### Step 4: Deploy on Railway (FREE!)

1. **Fork this GitHub repo** to your account

2. Go to https://railway.app and sign up

3. Click **"New Project"** → **"Deploy from GitHub repo"**

4. Select your forked repo

5. Click on the project → **"Variables"** tab

6. Add these 4 environment variables:

   ```
   API_ID = your_api_id
   API_HASH = your_api_hash
   SESSION_STRING = your_long_session_string
   TARGET_GROUP = https://t.me/+your_group_invite_link
   ```

7. Click **"Deploy"**

8. Check **"Deployments"** tab - should show "Success ✅"

9. Check **"Logs"** to see: `✅ Bot is running!`

### Step 5: Test It!

1. Have someone send you a message on Telegram
2. Check your backup group - message should appear instantly!
3. Even if they delete it, you have a copy! 🎉

## 🏃 Local Testing (Optional)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
TARGET_GROUP=https://t.me/+your_group_link
EOF

# Run it
python main.py
```

## 📱 How It Works

```
Someone sends you a message
        ↓
Bot catches it INSTANTLY
        ↓
Forwards to your backup group
        ↓
Shows: Name, Username, User ID, Profile Link
        ↓
Then forwards the actual message
```

## 🛠️ Configuration

Edit these in Railway Variables:

- `API_ID` - Your Telegram API ID
- `API_HASH` - Your Telegram API hash
- `SESSION_STRING` - Your session string
- `TARGET_GROUP` - Your backup group invite link

## 🔍 What Gets Forwarded

✅ Text messages  
✅ Photos & videos  
✅ Voice messages  
✅ Files & documents  
✅ Stickers & GIFs  
✅ Service messages (calls, etc.)  

❌ Does NOT forward:
- Messages FROM you
- Messages from bots
- Group messages
- Channel posts

## 📊 Logs

Check Railway logs to see:
```
✅ FORWARDED: John Doe (@johndoe) | User ID: 123456789
✅ FORWARDED: Jane Smith (@janesmith) | User ID: 987654321
```

## ⚙️ Files in This Repo

```
telegram-auto-forward/
├── main.py              # Main bot script
├── requirements.txt     # Python dependencies
├── .gitignore          # Prevents committing secrets
├── Procfile            # Railway config
├── README.md           # This file
└── .env.example        # Template for local setup
```

## ❓ Troubleshooting

**Bot not starting?**
- Check Railway logs for errors
- Verify all 4 environment variables are set
- Make sure SESSION_STRING is complete (very long string)

**Messages not forwarding?**
- Check if your account is in the backup group
- Verify TARGET_GROUP link is correct
- Look for errors in Railway logs

**"Session string invalid"?**
- Regenerate SESSION_STRING using generate_session.py
- Make sure you copied the entire string (no spaces/newlines)

## 📝 License

MIT License - Use freely!

## ⚠️ Disclaimer

- For personal backup purposes only
- Don't use to violate privacy
- Respect Telegram's Terms of Service
- You're responsible for how you use this

## 🆘 Support

Having issues? Check:
1. Railway logs for error messages
2. Make sure all variables are set correctly
3. Verify your SESSION_STRING is valid

---

**Made with ❤️ for message backup and protection against deletes!**

# ==================== Procfile ====================
worker: python main.py

# ==================== .env.example ====================
# Copy this to .env for local testing
# NEVER commit .env to GitHub!

# Get these from https://my.telegram.org
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Generate this using generate_session.py
SESSION_STRING=very_long_session_string_here

# Your backup group invite link
TARGET_GROUP=https://t.me/+ABC123xyz

# ==================== generate_session.py ====================
"""
Run this script ONCE to generate your SESSION_STRING
Keep the output SECRET!
"""

from pyrogram import Client

print("=" * 60)
print("🔐 Telegram Session String Generator")
print("=" * 60)
print()

API_ID = input("Enter your API_ID: ")
API_HASH = input("Enter your API_HASH: ")

print("\n📱 You'll receive a login code on Telegram...")

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

with app:
    session_string = app.export_session_string()
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Your SESSION_STRING:")
    print("=" * 60)
    print()
    print(session_string)
    print()
    print("=" * 60)
    print("⚠️  KEEP THIS SECRET! Never share it with anyone!")
    print("=" * 60)
