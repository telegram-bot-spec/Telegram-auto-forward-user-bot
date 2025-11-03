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

# Get environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
TARGET_GROUP = os.getenv('TARGET_GROUP', '-1002297717034')  # Your group chat ID

# Validate environment variables
if not API_ID or not API_HASH:
    logger.error("❌ ERROR: API_ID and API_HASH environment variables are required!")
    logger.error("Please set them in your environment.")
    sys.exit(1)

if not SESSION_STRING:
    logger.error("❌ ERROR: SESSION_STRING environment variable is required!")
    logger.error("Generate one using the generate_session.py script")
    sys.exit(1)

# Validate SESSION_STRING format
if len(SESSION_STRING) < 100:
    logger.error("❌ ERROR: SESSION_STRING appears to be too short (corrupted)!")
    logger.error(f"Current length: {len(SESSION_STRING)} characters")
    logger.error("Please regenerate your session string using generate_session.py")
    sys.exit(1)

# Create client
try:
    app = Client(
        "auto_forward_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
    logger.info("✅ Client created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create client: {e}")
    sys.exit(1)

def get_user_info(user):
    """Generate detailed user information with clickable links"""
    
    # Basic info
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    user_id = user.id
    username = user.username
    
    # Build info message
    info_lines = []
    info_lines.append(f"👤 **From:** {full_name}")
    info_lines.append(f"🆔 **User ID:** `{user_id}`")
    
    # Add username if available
    if username:
        info_lines.append(f"📝 **Username:** @{username}")
        info_lines.append(f"🔗 **Profile:** [Open Profile](https://t.me/{username})")
    else:
        # If no username, use tg://user?id= link (opens in Telegram app)
        info_lines.append(f"📝 **Username:** Not set")
        info_lines.append(f"🔗 **Profile:** [Open Profile](tg://user?id={user_id})")
    
    # Add additional info if available
    if user.is_verified:
        info_lines.append("✅ **Verified Account**")
    if user.is_premium:
        info_lines.append("⭐ **Premium User**")
    if user.is_bot:
        info_lines.append("🤖 **Bot Account**")
    
    info_lines.append("─" * 30)
    
    return "\n".join(info_lines)

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot)
async def forward_to_group(client: Client, message: Message):
    """Forward every incoming private message to the target group with user info"""
    try:
        user = message.from_user
        
        # Get detailed user info
        user_info = get_user_info(user)
        
        # Send user info first to the group
        await client.send_message(TARGET_GROUP, user_info, disable_web_page_preview=False)
        
        # Forward the actual message to the group
        await message.forward(TARGET_GROUP)
        
        logger.info(f"✅ Forwarded message from {user.first_name} (ID: {user.id}, Username: @{user.username or 'None'}) to group {TARGET_GROUP}")
        
    except Exception as e:
        logger.error(f"❌ Error forwarding message: {e}")
        logger.error(f"   Make sure the bot account is a member of the group: {TARGET_GROUP}")

@app.on_message(filters.private & filters.incoming & ~filters.me & filters.service)
async def forward_service_messages(client: Client, message: Message):
    """Also forward service messages like voice calls, etc."""
    try:
        user = message.from_user
        user_info = get_user_info(user)
        
        await client.send_message(TARGET_GROUP, user_info + "\n📞 **Service Message**", disable_web_page_preview=False)
        await message.forward(TARGET_GROUP)
        
        logger.info(f"✅ Forwarded service message from {user.first_name} (ID: {user.id}) to group {TARGET_GROUP}")
        
    except Exception as e:
        logger.error(f"❌ Error forwarding service message: {e}")
        logger.error(f"   Make sure the bot account is a member of the group: {TARGET_GROUP}")

if __name__ == "__main__":
    logger.info("🚀 Starting Auto-Forward UserBot...")
    logger.info(f"📨 All incoming messages will be forwarded to group: {TARGET_GROUP}")
    logger.info("✨ Enhanced with detailed user information and clickable profile links")
    
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("If you see 'struct.error' or session errors, regenerate your SESSION_STRING")
        sys.exit(1)
