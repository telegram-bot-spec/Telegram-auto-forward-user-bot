import os
import sys
import logging
from pyrogram import Client
from pyrogram.enums import ChatType
import json
from datetime import datetime

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

# Validate environment variables
if not API_ID or not API_HASH or not SESSION_STRING:
    logger.error("❌ ERROR: Required environment variables are missing!")
    logger.error("Please set: API_ID, API_HASH, SESSION_STRING")
    logger.error("\nFor Railway deployment:")
    logger.error("1. Go to your Railway project")
    logger.error("2. Click on 'Variables' tab")
    logger.error("3. Add these three variables with your values")
    sys.exit(1)

# Validate SESSION_STRING format
if len(SESSION_STRING) < 100:
    logger.error("❌ ERROR: SESSION_STRING appears invalid (too short)")
    logger.error("Please regenerate using generate_session.py")
    sys.exit(1)

# Create client
try:
    app = Client(
        "private_msg_exporter",
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

async def export_all_private_messages():
    """Export ALL private messages from ALL users"""
    try:
        async with app:
            logger.info("✅ Connected to Telegram")
            
            # Create output directory
            output_dir = "private_messages_export"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            all_chats_file = f"{output_dir}/all_private_chats_{timestamp}.json"
            summary_file = f"{output_dir}/summary_{timestamp}.txt"
            
            all_data = []
            total_messages = 0
            total_chats = 0
            
            logger.info("🔍 Scanning all private chats...")
            
            # Get all dialogs (conversations)
            async for dialog in app.get_dialogs():
                # Only process PRIVATE chats (1-on-1 conversations with users)
                if dialog.chat.type == ChatType.PRIVATE:
                    chat = dialog.chat
                    total_chats += 1
                    
                    user_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip()
                    username = f"@{chat.username}" if chat.username else "No username"
                    
                    logger.info(f"\n📱 Processing chat {total_chats}: {user_name} ({username})")
                    logger.info(f"   User ID: {chat.id}")
                    
                    chat_data = {
                        "user_info": {
                            "id": chat.id,
                            "first_name": chat.first_name,
                            "last_name": chat.last_name,
                            "username": chat.username,
                            "is_verified": chat.is_verified if hasattr(chat, 'is_verified') else False,
                            "is_premium": chat.is_premium if hasattr(chat, 'is_premium') else False,
                            "is_bot": chat.is_bot if hasattr(chat, 'is_bot') else False
                        },
                        "messages": []
                    }
                    
                    message_count = 0
                    
                    # Get all messages from this chat
                    async for message in app.get_chat_history(chat.id):
                        message_count += 1
                        
                        msg_data = {
                            "id": message.id,
                            "date": message.date.isoformat() if message.date else None,
                            "from_me": message.outgoing,
                            "text": message.text,
                            "caption": message.caption,
                            "media_type": str(message.media) if message.media else None
                        }
                        
                        chat_data["messages"].append(msg_data)
                        
                        if message_count % 50 == 0:
                            logger.info(f"   📊 Fetched {message_count} messages...")
                    
                    total_messages += message_count
                    logger.info(f"   ✅ Total messages in this chat: {message_count}")
                    
                    all_data.append(chat_data)
                    
                    # Save individual chat to separate file
                    safe_username = (chat.username or 'no_username').replace('/', '_')
                    individual_file = f"{output_dir}/chat_{chat.id}_{safe_username}_{timestamp}.json"
                    with open(individual_file, 'w', encoding='utf-8') as f:
                        json.dump(chat_data, f, indent=2, ensure_ascii=False)
                    
                    # Also create readable text file for this chat
                    txt_file = f"{output_dir}/chat_{chat.id}_{safe_username}_{timestamp}.txt"
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(f"CHAT WITH: {user_name}\n")
                        f.write(f"USERNAME: {username}\n")
                        f.write(f"USER ID: {chat.id}\n")
                        f.write(f"TOTAL MESSAGES: {message_count}\n")
                        f.write(f"EXPORTED: {datetime.now()}\n")
                        f.write("=" * 80 + "\n\n")
                        
                        for msg in reversed(chat_data["messages"]):
                            f.write(f"[{msg['date']}]\n")
                            f.write(f"{'📤 YOU' if msg['from_me'] else '📥 ' + user_name}: ")
                            
                            if msg['text']:
                                f.write(f"{msg['text']}\n")
                            elif msg['caption']:
                                f.write(f"{msg['caption']}\n")
                            elif msg['media_type']:
                                f.write(f"[{msg['media_type']}]\n")
                            else:
                                f.write("[Message]\n")
                            
                            f.write("-" * 80 + "\n\n")
            
            # Save combined JSON with all chats
            with open(all_chats_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            # Create summary file
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("TELEGRAM PRIVATE MESSAGES EXPORT SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Export Date: {datetime.now()}\n")
                f.write(f"Total Private Chats: {total_chats}\n")
                f.write(f"Total Messages: {total_messages}\n\n")
                f.write("=" * 80 + "\n\n")
                f.write("CHATS:\n\n")
                
                for idx, chat_data in enumerate(all_data, 1):
                    user = chat_data['user_info']
                    name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip()
                    username = f"@{user['username']}" if user['username'] else "No username"
                    msg_count = len(chat_data['messages'])
                    
                    f.write(f"{idx}. {name} ({username})\n")
                    f.write(f"   User ID: {user['id']}\n")
                    f.write(f"   Messages: {msg_count}\n")
                    if user['is_verified']:
                        f.write(f"   ✅ Verified\n")
                    if user['is_premium']:
                        f.write(f"   ⭐ Premium\n")
                    if user['is_bot']:
                        f.write(f"   🤖 Bot\n")
                    f.write("\n")
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✅ EXPORT COMPLETED!")
            logger.info(f"📊 Total private chats exported: {total_chats}")
            logger.info(f"💬 Total messages exported: {total_messages}")
            logger.info(f"📁 Files saved in: {output_dir}/")
            logger.info("=" * 80)
            
    except Exception as e:
        logger.error(f"❌ Error during export: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("🚀 Starting PRIVATE Messages Exporter...")
    logger.info("📱 This will export ALL private messages from ALL users")
    logger.info("⏳ This may take a while depending on how many chats you have...\n")
    
    import asyncio
    asyncio.run(export_all_private_messages())
