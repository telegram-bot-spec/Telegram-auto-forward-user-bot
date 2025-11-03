import os
import sys
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables (NEVER hardcode these!)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

# Your private group link - convert to chat ID after first run
# Put your group invite link here or the group ID (like -1001234567890)
TARGET_GROUP = os.getenv('TARGET_GROUP', 'https://t.me/+rGX0kTfm9lI1YzFl')

# Validate environment variables
if not API_ID or not API_HASH or not SESSION_STRING:
    logger.error("❌ ERROR: Required environment variables are missing!")
    logger.error("Please set: API_ID, API_HASH, SESSION_STRING")
    logger.error("\nFor Railway deployment:")
    logger.error("1. Go to your Railway project")
    logger.error("2. Click on 'Variables' tab")
    logger.error("3. Add these variables with your values")
    sys.exit(1)

# Validate SESSION_STRING format
if len(SESSION_STRING) < 100:
    logger.error("❌ ERROR: SESSION_STRING appears invalid (too short)")
    sys.exit(1)

# Create client
try:
    app = Client(
        "auto_forward_bot",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
    logger.info("✅ Client created successfully")
except ValueError:
    logger.error("❌ ERROR: API_ID must be a number")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Failed to create client: {e}")
    sys.exit(1)

# Store the actual chat ID after joining
actual_group_id = None

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot)
async def forward_private_messages(client: Client, message: Message):
    """
    Auto-forward EVERY incoming private message to the target group
    This catches messages INSTANTLY before they can be deleted!
    """
    global actual_group_id
    
    try:
        user = message.from_user
        
        # Build user info
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        username = f"@{user.username}" if user.username else "No username"
        user_id = user.id
        
        # Create detailed info message
        info_lines = []
        info_lines.append("🔔 **NEW MESSAGE RECEIVED**")
        info_lines.append("━━━━━━━━━━━━━━━━━━━━")
        info_lines.append(f"👤 **From:** {full_name}")
        info_lines.append(f"🆔 **User ID:** `{user_id}`")
        info_lines.append(f"📝 **Username:** {username}")
        
        if user.username:
            info_lines.append(f"🔗 **Profile:** https://t.me/{user.username}")
        else:
            info_lines.append(f"🔗 **Profile:** tg://user?id={user_id}")
        
        if user.is_verified:
            info_lines.append("✅ **Verified Account**")
        if user.is_premium:
            info_lines.append("⭐ **Premium User**")
        if user.is_bot:
            info_lines.append("🤖 **Bot Account**")
        
        info_lines.append("━━━━━━━━━━━━━━━━━━━━")
        
        user_info = "\n".join(info_lines)
        
        # Send user info first
        await client.send_message(actual_group_id, user_info, disable_web_page_preview=False)
        
        # Forward the actual message immediately
        await message.forward(actual_group_id)
        
        logger.info(f"✅ FORWARDED: {full_name} ({username}) | User ID: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to forward message: {e}")
        logger.error(f"   From: {user.first_name if user else 'Unknown'}")

@app.on_message(filters.private & filters.incoming & ~filters.me & filters.service)
async def forward_service_messages(client: Client, message: Message):
    """
    Also forward service messages (calls, voice chats, etc.)
    """
    global actual_group_id
    
    try:
        user = message.from_user
        
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        username = f"@{user.username}" if user.username else "No username"
        
        service_info = f"📞 **SERVICE MESSAGE**\n"
        service_info += f"👤 From: {full_name} ({username})\n"
        service_info += f"🆔 User ID: `{user.id}`"
        
        await client.send_message(actual_group_id, service_info)
        await message.forward(actual_group_id)
        
        logger.info(f"✅ FORWARDED SERVICE: {full_name} ({username})")
        
    except Exception as e:
        logger.error(f"❌ Failed to forward service message: {e}")

async def initialize():
    """Initialize and join the target group"""
    global actual_group_id
    
    try:
        # If TARGET_GROUP is a link, join it
        if TARGET_GROUP.startswith('https://t.me/'):
            logger.info(f"🔗 Joining group via invite link...")
            chat = await app.join_chat(TARGET_GROUP)
            actual_group_id = chat.id
            logger.info(f"✅ Joined group: {chat.title}")
            logger.info(f"📊 Group ID: {actual_group_id}")
        else:
            # Already a chat ID
            actual_group_id = TARGET_GROUP
            chat = await app.get_chat(actual_group_id)
            logger.info(f"✅ Using existing group: {chat.title}")
            logger.info(f"📊 Group ID: {actual_group_id}")
        
        # Send startup message to group
        startup_msg = "🚀 **AUTO-FORWARD BOT STARTED**\n"
        startup_msg += "━━━━━━━━━━━━━━━━━━━━\n"
        startup_msg += "✅ Bot is now ONLINE\n"
        startup_msg += "📱 All incoming private messages will be forwarded here\n"
        startup_msg += "⚡ Messages are captured INSTANTLY\n"
        startup_msg += "🛡️ Even deleted messages will be saved here\n"
        startup_msg += "━━━━━━━━━━━━━━━━━━━━"
        
        await app.send_message(actual_group_id, startup_msg)
        
    except Exception as e:
        logger.error(f"❌ Failed to join/access group: {e}")
        logger.error("Make sure:")
        logger.error("1. The invite link is correct")
        logger.error("2. Your account has permission to join")
        logger.error("3. You're the group owner/admin")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 TELEGRAM AUTO-FORWARD BOT")
    logger.info("=" * 60)
    logger.info("📱 Mode: LIVE FORWARDING (New messages only)")
    logger.info("🎯 Target: All incoming private messages")
    logger.info(f"📊 Forward to: {TARGET_GROUP}")
    logger.info("⚡ Speed: INSTANT (before deletion)")
    logger.info("=" * 60)
    
    try:
        # Start the client with initialization
        with app:
            import asyncio
            asyncio.get_event_loop().run_until_complete(initialize())
            logger.info("\n✅ Bot is running! Press Ctrl+C to stop.\n")
            app.run()
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
