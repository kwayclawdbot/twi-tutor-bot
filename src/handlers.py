"""
Twi Tutor Bot - Command and Message Handlers
"""
import logging
import os
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from src.config import config
from src.database import db
from src.ai_service import ai_service
from src.keyboards import (
    get_main_menu_keyboard,
    get_lessons_menu_keyboard,
    get_lessons_list_keyboard,
    get_lesson_action_keyboard,
    get_practice_mode_keyboard,
    get_progress_view_keyboard,
    get_help_keyboard,
    get_conversation_continue_keyboard,
)

logger = logging.getLogger(__name__)


# ==================== START & MENU ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Welcome new users"""
    user = update.effective_user
    
    # Get or create user in database
    db_user = await db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Store user context
    context.user_data['user_id'] = db_user['id']
    context.user_data['telegram_id'] = user.id
    
    welcome_text = f"""
🌟 **Akwaaba! Nana Akosua is happy to meet you!** 🌟

Akwaaba, {user.first_name or 'me ba'}! (Welcome, my child!)

Wo ho te sɛn? (How are you?)

I'm Nana Akosua, your Twi teacher from Kumasi, Ghana. I'll guide you on a wonderful journey to learn Twi - not just words, but the heart and soul of Ghanaian culture.

**How we learn together:**
🎤 **Voice-first** - Send me voice messages! I'll listen and respond
📚 **Structured lessons** - From greetings to conversations
🇬🇭 **Cultural stories** - Every word connects to our heritage
📊 **Track progress** - Watch yourself grow

Ready to begin?
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    
    # Send voice greeting
    voice_text = f"Akwaaba, {user.first_name or 'me ba'}! Welcome to your Twi learning journey. I'm Nana Akosua, and I'm so happy you'll be learning with me. Send me a voice message or tap Lessons to begin!"
    audio_path = await ai_service.generate_voice(voice_text)
    if audio_path and os.path.exists(audio_path):
        with open(audio_path, 'rb') as audio:
            await update.message.reply_voice(audio)
        os.remove(audio_path)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🆘 **Twi Tutor Help** 🆘

**Commands:**
/start - Begin your journey
/lesson - Start or continue lessons  
/progress - View your learning stats
/practice - Free practice mode
/help - Show this help

**Tips:**
🎤 Send voice messages in Twi for pronunciation practice
📱 Use the menu buttons to navigate
⭐ Save vocabulary words you want to review

**How to pronounce Twi:**
- 'ɛ' sounds like 'e' in 'bed'
- 'ɔ' sounds like 'o' in 'hot'  
- 'ny' sounds like 'ñ' in Spanish
- Tone is important!

Need more help? Just ask!
"""
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_help_keyboard(),
        parse_mode='Markdown'
    )


async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lesson command"""
    categories = await db.get_all_categories()
    
    text = """
📚 **Twi Lessons** 📚

Choose a category to explore:

Each lesson includes:
✅ New vocabulary with pronunciation
✅ Cultural context and stories  
✅ Practice exercises
✅ Pronunciation tips
"""
    
    await update.message.reply_text(
        text,
        reply_markup=get_lessons_menu_keyboard(categories),
        parse_mode='Markdown'
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command"""
    if 'user_id' not in context.user_data:
        await update.message.reply_text("Please start with /start first!")
        return
    
    user_id = context.user_data['user_id']
    stats = await db.get_user_stats(user_id)
    
    progress_text = f"""
📊 **Your Progress** 📊

🔥 **Streak:** {stats['streak']} days
📚 **Lessons Completed:** {stats['lessons_completed']}
⏱️ **Total Practice:** {stats['total_minutes']} minutes
📈 **Level:** {stats['level'].title()}

Keep going! Every moment of practice brings you closer to mastery!
"""
    
    await update.message.reply_text(
        progress_text,
        reply_markup=get_progress_view_keyboard(),
        parse_mode='Markdown'
    )


async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /practice command"""
    text = """
🎯 **Practice Mode** 🎯

Choose how you'd like to practice:

Send me voice messages and I'll help you improve your pronunciation!
"""
    
    await update.message.reply_text(
        text,
        reply_markup=get_practice_mode_keyboard(),
        parse_mode='Markdown'
    )


async def vocab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /vocab command"""
    if 'user_id' not in context.user_data:
        await update.message.reply_text("Please start with /start first!")
        return
    
    user_id = context.user_data['user_id']
    vocab = await db.get_user_vocabulary(user_id, limit=10)
    
    if not vocab:
        text = """
⭐ **Your Vocabulary** ⭐

Your vocabulary deck is empty!

Start lessons to add words, or tap below to practice common words.
"""
    else:
        text = "⭐ **Your Vocabulary** ⭐\n\n"
        for item in vocab:
            star = "⭐" if item.get('is_starred') else ""
            text += f"{star} **{item['word_twi']}** - {item['word_english']}\n"
            if item.get('pronunciation'):
                text += f"   _{item['pronunciation']}_\n"
        text += "\nTap any word to practice or review!"
    
    await update.message.reply_text(text, parse_mode='Markdown')


# ==================== MESSAGE HANDLERS ====================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    if 'user_id' not in context.user_data:
        await update.message.reply_text("Please start with /start first!")
        return
    
    user_message = update.message.text
    user_id = context.user_data['user_id']
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    # Get conversation history
    history = await db.get_conversation_history(user_id, limit=10)
    
    messages = []
    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})
    messages.append({"role": "user", "content": user_message})
    
    system_prompt = """You are Nana Akosua, a warm Ghanaian elder teaching Twi. 

Respond in this format ALWAYS:
[TWI RESPONSE]

[ENGLISH TRANSLATION]

[CULTURAL NOTE when relevant]

Be encouraging, patient, and weave cultural stories into teaching."""
    
    response = await ai_service.generate_response(messages, system_prompt)
    
    # Save conversation
    await db.save_message(user_id, 'user', user_message)
    await db.save_message(user_id, 'assistant', response)
    await db.log_daily_activity(user_id, message_count=2)
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Generate voice response
    audio_path = await ai_service.generate_voice(response)
    if audio_path and os.path.exists(audio_path):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_VOICE
        )
        with open(audio_path, 'rb') as audio:
            await update.message.reply_voice(audio)
        os.remove(audio_path)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    if 'user_id' not in context.user_data:
        await update.message.reply_text("Please start with /start first!")
        return
    
    user_id = context.user_data['user_id']
    
    # Download voice file
    voice_file = await update.message.voice.get_file()
    
    if update.message.voice.duration > config.MAX_VOICE_DURATION:
        await update.message.reply_text(
            f"🎤 Your message is a bit long! Please keep voice messages under {config.MAX_VOICE_DURATION} seconds."
        )
        return
    
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    # Save to temp file
    temp_path = os.path.join(config.AUDIO_STORAGE_PATH, f"voice_{user.id}_{update.message.message_id}.ogg")
    await voice_file.download_to_drive(temp_path)
    
    # Transcribe
    transcription, confidence = await ai_service.transcribe_voice(temp_path)
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    if not transcription:
        await update.message.reply_text(
            "🎤 Me nsɛm tie... (I couldn't hear well...)\n\nCould you try speaking a bit louder or clearer? Or send me a text message!"
        )
        return
    
    # Get conversation history
    history = await db.get_conversation_history(user_id, limit=10)
    
    messages = []
    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})
    
    messages.append({
        "role": "user", 
        "content": f"[VOICE MESSAGE - TRANSCRIBED]: {transcription}"
    })
    
    system_prompt = """You are Nana Akosua, a warm Ghanaian elder teaching Twi. 

The user sent a VOICE message (transcribed above). Praise their effort for speaking!

Respond in this format:
[TWI RESPONSE]

[ENGLISH TRANSLATION]

[PRONUNCIATION FEEDBACK - gentle suggestions]

[CULTURAL NOTE]

Be very encouraging - learning to speak takes courage!"""
    
    response = await ai_service.generate_response(messages, system_prompt)
    
    # Save conversation
    await db.save_message(user_id, 'user', transcription, was_transcribed=True)
    await db.save_message(user_id, 'assistant', response)
    await db.log_daily_activity(user_id, message_count=2, voice_sent=True)
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Generate voice response
    audio_path = await ai_service.generate_voice(response)
    if audio_path and os.path.exists(audio_path):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_VOICE
        )
        with open(audio_path, 'rb') as audio:
            await update.message.reply_voice(audio)
        os.remove(audio_path)


# ==================== CALLBACK HANDLERS ====================

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'menu_lessons':
        categories = await db.get_all_categories()
        await query.edit_message_text(
            "📚 **Twi Lessons**\n\nChoose a category:",
            reply_markup=get_lessons_menu_keyboard(categories),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_progress':
        await progress_command(update, context)
    
    elif data == 'menu_practice':
        await practice_command(update, context)
    
    elif data == 'menu_help':
        await help_command(update, context)
    
    elif data.startswith('cat_'):
        category_slug = data.replace('cat_', '')
        lessons = await db.get_lessons_by_category(category_slug)
        
        await query.edit_message_text(
            f"📚 **{category_slug.title()} Lessons**\n\nChoose a lesson:",
            reply_markup=get_lessons_list_keyboard(lessons),
            parse_mode='Markdown'
        )
    
    elif data.startswith('lesson_'):
        lesson_slug = data.replace('lesson_', '')
        lesson = await db.get_lesson_by_slug(lesson_slug)
        
        if lesson:
            vocab_text = "\n".join([
                f"• {v.get('word', '')} - {v.get('meaning', '')}"
                for v in lesson.get('vocabulary', [])[:5]
            ])
            
            text = f"""
📖 **{lesson['name']}** ({lesson.get('name_twi', '')})

{vocab_text}

Tap Start to begin!
"""
            await query.edit_message_text(
                text,
                reply_markup=get_lesson_action_keyboard(lesson_slug),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("Lesson not found. Try again!")
    
    elif data == 'back_menu':
        await query.edit_message_text(
            "🌟 **Main Menu**\n\nWhat would you like to do?",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == 'back_lessons':
        categories = await db.get_all_categories()
        await query.edit_message_text(
            "📚 **Twi Lessons**\n\nChoose a category:",
            reply_markup=get_lessons_menu_keyboard(categories),
            parse_mode='Markdown'
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Me kronrono... (I'm sorry...)\n\nSomething went wrong. Please try again!"
        )
