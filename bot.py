"""
Twi Tutor Bot - Main Entry Point
"""
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from src.config import config
from src.handlers import (
    start_command,
    help_command,
    lesson_command,
    progress_command,
    practice_command,
    vocab_command,
    handle_text_message,
    handle_voice_message,
    handle_callback_query,
    error_handler,
)

# Configure logging
logging.basicConfig(
    format=config.LOG_FORMAT,
    level=getattr(logging, config.LOG_LEVEL.upper()),
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot"""
    logger.info("🚀 Starting Twi Tutor Bot...")
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lesson", lesson_command))
    application.add_handler(CommandHandler("lessons", lesson_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("practice", practice_command))
    application.add_handler(CommandHandler("vocab", vocab_command))
    application.add_handler(CommandHandler("vocabulary", vocab_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
