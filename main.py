import os
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

# Create client
app = Client(
    "auto_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot)
async def forward_to_saved(client: Client, message: Message):
    """Forward every incoming private message to Saved Messages"""
    try:
        # Forward to Saved Messages (your own chat)
        await message.forward("me")
        
        logger.info(f"Forwarded message from {message.from_user.id} ({message.from_user.first_name})")
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")

@app.on_message(filters.private & filters.incoming & ~filters.me & filters.service)
async def forward_service_messages(client: Client, message: Message):
    """Also forward service messages like voice calls, etc."""
    try:
        await message.forward("me")
        logger.info(f"Forwarded service message from {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error forwarding service message: {e}")

if __name__ == "__main__":
    logger.info("Starting Auto-Forward UserBot...")
    logger.info("All incoming messages will be forwarded to Saved Messages!")
    app.run()
