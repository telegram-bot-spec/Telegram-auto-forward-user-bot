import os
import sys
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UsernameInvalid, UsernameNotOccupied, ChannelPrivate
from pyrogram.enums import ParseMode
import asyncio

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
TARGET_GROUP = os.getenv('TARGET_GROUP', '@logsbackupofall')

# Validate environment variables
if not all([API_ID, API_HASH, SESSION_STRING]):
    logger.error("❌ ERROR: Missing required environment variables!")
    logger.error("\nRequired variables:")
    logger.error("  - API_ID (get from https://my.telegram.org)")
    logger.error("  - API_HASH (get from https://my.telegram.org)")
    logger.error("  - SESSION_STRING (generate using session generator)")
    logger.error("  - TARGET_GROUP (your group @username)")
    logger.error("\nFor Railway deployment:")
    logger.error("  1. Go to your Railway project")
    logger.error("  2. Click 'Variables' tab")
    logger.error("  3. Add all variables above")
    sys.exit(1)

# Validate SESSION_STRING
if len(SESSION_STRING) < 100:
    logger.error("❌ ERROR: SESSION_STRING appears invalid (too short)")
    logger.error("Generate a new session string using Pyrogram's session generator")
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
except ValueError as e:
    logger.error(f"❌ ERROR: API_ID must be a valid number: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Failed to create client: {e}")
    sys.exit(1)

# Global variable for group chat ID
target_chat_id = None


def clean_username(username: str) -> str:
    """Clean and normalize username"""
    username = username.strip()
    # Remove common prefixes
    if username.startswith('https://t.me/'):
        username = username.replace('https://t.me/', '')
    if username.startswith('@'):
        username = username[1:]
    # Remove any trailing slashes
    username = username.rstrip('/')
    return username


async def resolve_target_group():
    """Resolve target group and return chat ID"""
    global target_chat_id
    
    try:
        target = TARGET_GROUP.strip()
        logger.info(f"🔍 Resolving target: {target}")
        
        # Case 1: Already a numeric ID
        if target.lstrip('-').isdigit():
            target_chat_id = int(target)
            logger.info(f"✅ Using numeric ID: {target_chat_id}")
            
            # Verify access
            try:
                chat = await app.get_chat(target_chat_id)
                logger.info(f"✅ Verified group: {chat.title}")
                return target_chat_id
            except Exception as e:
                logger.error(f"❌ Cannot access group with ID {target_chat_id}: {e}")
                raise
        
        # Case 2: Private invite link
        elif 'https://t.me/+' in target or 'https://t.me/joinchat/' in target:
            logger.info("🔗 Detected private invite link")
            try:
                chat = await app.join_chat(target)
                target_chat_id = chat.id
                logger.info(f"✅ Joined group: {chat.title} (ID: {target_chat_id})")
                return target_chat_id
            except Exception as e:
                logger.error(f"❌ Failed to join via invite link: {e}")
                logger.info("🔍 Checking if already a member...")
                
                # Search in existing dialogs
                try:
                    async for dialog in app.get_dialogs():
                        if dialog.chat.type in ["group", "supergroup"]:
                            if hasattr(dialog.chat, 'invite_link') and dialog.chat.invite_link:
                                if target in str(dialog.chat.invite_link):
                                    target_chat_id = dialog.chat.id
                                    logger.info(f"✅ Found group: {dialog.chat.title} (ID: {target_chat_id})")
                                    return target_chat_id
                except Exception as search_error:
                    logger.warning(f"⚠️ Search error: {search_error}")
                
                raise Exception("Could not join or find group. Join manually first, then use group ID or username.")
        
        # Case 3: Username (with or without @)
        else:
            username = clean_username(target)
            
            if len(username) > 32:
                logger.error(f"❌ Username too long: '{username}' ({len(username)} chars)")
                logger.error("Telegram usernames must be ≤32 characters")
                raise ValueError("Username exceeds 32 character limit")
            
            if not username:
                raise ValueError("Empty username after cleaning")
            
            logger.info(f"🔍 Looking up username: @{username}")
            
            try:
                chat = await app.get_chat(username)
                target_chat_id = chat.id
                logger.info(f"✅ Found group: {chat.title} (ID: {target_chat_id})")
                return target_chat_id
            except UsernameInvalid:
                logger.error(f"❌ Invalid username: @{username}")
                raise
            except UsernameNotOccupied:
                logger.error(f"❌ Username not found: @{username}")
                logger.error("Make sure the group has a public username set")
                raise
            except ChannelPrivate:
                logger.error(f"❌ Group is private. Use invite link or join manually first")
                raise
            except Exception as e:
                logger.error(f"❌ Error looking up username: {e}")
                raise
    
    except Exception as e:
        logger.error(f"\n{'='*60}")
        logger.error("❌ FAILED TO ACCESS TARGET GROUP")
        logger.error(f"{'='*60}")
        logger.error(f"Error: {e}")
        logger.error(f"\n📋 Current TARGET_GROUP: {TARGET_GROUP}")
        logger.error("\n✅ SOLUTIONS:")
        logger.error("\n1. Use Group Username (EASIEST):")
        logger.error("   - Open group in Telegram")
        logger.error("   - Go to: Group Info → Edit → Username")
        logger.error("   - Set a username (max 32 chars)")
        logger.error("   - Set TARGET_GROUP=@yourusername")
        logger.error("\n2. Use Group ID:")
        logger.error("   - Forward any message from the group to @userinfobot")
        logger.error("   - Copy the chat ID (e.g., -1001234567890)")
        logger.error("   - Set TARGET_GROUP=-1001234567890")
        logger.error("\n3. Use Private Invite Link:")
        logger.error("   - Get group invite link: Group Info → Invite Link")
        logger.error("   - Set TARGET_GROUP=https://t.me/+xxxxx")
        logger.error(f"{'='*60}\n")
        raise


@app.on_message(filters.private & filters.incoming & ~filters.me)
async def forward_private_messages(client: Client, message: Message):
    """Forward ALL incoming private messages to target group"""
    
    if target_chat_id is None:
        logger.error("❌ Target chat ID not initialized!")
        return
    
    try:
        user = message.from_user
        
        # Check if user exists (for very rare edge cases)
        if not user:
            logger.warning("⚠️ Received message with no user info")
            return
        
        # Handle service messages differently
        if message.service:
            await forward_service_message(client, message)
            return
        
        # Build user info - HTML escape special characters
        import html
        first_name = html.escape(user.first_name or "")
        last_name = html.escape(user.last_name or "")
        full_name = f"{first_name} {last_name}".strip() or "Unknown"
        username = f"@{user.username}" if user.username else "No username"
        user_id = user.id
        
        # Create info message with HTML formatting for clickable mention
        info_parts = [
            "🔔 <b>NEW MESSAGE RECEIVED</b>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"👤 <b>From:</b> <a href='tg://user?id={user_id}'>{full_name}</a>",
            f"🆔 <b>User ID:</b> <code>{user_id}</code>",
            f"📝 <b>Username:</b> {username}",
        ]
        
        # Add profile link
        if user.username:
            info_parts.append(f"🔗 <b>Profile:</b> https://t.me/{user.username}")
        else:
            info_parts.append(f"🔗 <b>Profile:</b> <a href='tg://user?id={user_id}'>Click to open profile</a>")
        
        # Add badges
        if user.is_verified:
            info_parts.append("✅ <b>Verified Account</b>")
        if user.is_premium:
            info_parts.append("⭐ <b>Premium User</b>")
        if user.is_bot:
            info_parts.append("🤖 <b>Bot Account</b>")
        
        info_parts.append("━━━━━━━━━━━━━━━━━━━━")
        
        user_info = "\n".join(info_parts)
        
        # Send info message with HTML parse mode
        await client.send_message(
            target_chat_id,
            user_info,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        # Forward the actual message
        await message.forward(target_chat_id)
        
        logger.info(f"✅ Forwarded from: {full_name} (@{user.username or 'none'}) | ID: {user_id}")
        
    except FloodWait as e:
        logger.warning(f"⏳ FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
        # Retry
        await forward_private_messages(client, message)
    except Exception as e:
        logger.error(f"❌ Forward failed: {e}")
        try:
            if user:
                logger.error(f"   User: {user.first_name or 'Unknown'} (ID: {user.id})")
        except:
            pass


async def forward_service_message(client: Client, message: Message):
    """Forward service messages (calls, video chats, etc.)"""
    
    try:
        user = message.from_user
        
        if not user:
            logger.warning("⚠️ Service message with no user info")
            return
        
        # HTML escape special characters
        import html
        first_name = html.escape(user.first_name or "")
        last_name = html.escape(user.last_name or "")
        full_name = f"{first_name} {last_name}".strip() or "Unknown"
        username = f"@{user.username}" if user.username else "No username"
        
        # Clickable mention for service messages with HTML
        service_info = (
            f"📞 <b>SERVICE MESSAGE</b>\n"
            f"👤 <b>From:</b> <a href='tg://user?id={user.id}'>{full_name}</a> ({username})\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>"
        )
        
        await client.send_message(
            target_chat_id,
            service_info,
            parse_mode=ParseMode.HTML
        )
        await message.forward(target_chat_id)
        
        logger.info(f"✅ Forwarded service message from: {full_name}")
        
    except Exception as e:
        logger.error(f"❌ Service message forward failed: {e}")
        try:
            if user:
                logger.error(f"   User ID: {user.id}")
        except:
            pass


async def send_startup_message():
    """Send startup notification to group"""
    try:
        if target_chat_id is None:
            logger.warning("⚠️ Cannot send startup message: target_chat_id is None")
            return
            
        startup_msg = (
            "🚀 <b>AUTO-FORWARD BOT STARTED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ Bot is now ONLINE\n"
            "📱 All incoming private messages will be forwarded here\n"
            "⚡ Messages captured INSTANTLY\n"
            "🛡️ Even deleted messages will be saved\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        await app.send_message(
            target_chat_id,
            startup_msg,
            parse_mode=ParseMode.HTML
        )
        logger.info("✅ Startup notification sent")
    except Exception as e:
        logger.warning(f"⚠️ Could not send startup message: {e}")


async def main():
    """Main async function"""
    global target_chat_id
    
    logger.info("=" * 60)
    logger.info("🚀 TELEGRAM AUTO-FORWARD BOT")
    logger.info("=" * 60)
    logger.info("📱 Mode: LIVE FORWARDING")
    logger.info("🎯 Target: All incoming private messages")
    logger.info(f"📊 Forward to: {TARGET_GROUP}")
    logger.info("⚡ Speed: INSTANT (before deletion)")
    logger.info("=" * 60)
    
    try:
        await app.start()
        logger.info("✅ Client started")
    except Exception as e:
        logger.error(f"❌ Failed to start client: {e}")
        logger.error("Check your SESSION_STRING, API_ID, and API_HASH")
        raise
    
    # Resolve target group
    try:
        await resolve_target_group()
    except Exception as e:
        logger.error("❌ Cannot continue without valid target group")
        try:
            await app.stop()
        except:
            pass
        sys.exit(1)
    
    # Send startup message
    await send_startup_message()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ BOT IS RUNNING!")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop\n")
    
    # Keep running until interrupted
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("🛑 Shutting down gracefully...")
        raise


if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
