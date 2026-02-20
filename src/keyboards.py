"""
Twi Tutor Bot - Keyboard Utilities
Inline and reply keyboards for Telegram
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any, Optional

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu inline keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📚 Lessons", callback_data='menu_lessons'),
            InlineKeyboardButton("📊 My Progress", callback_data='menu_progress')
        ],
        [
            InlineKeyboardButton("🎯 Practice", callback_data='menu_practice'),
            InlineKeyboardButton("🔊 Conversation", callback_data='menu_conversation')
        ],
        [
            InlineKeyboardButton("⭐ My Vocabulary", callback_data='menu_vocab'),
            InlineKeyboardButton("🏆 Achievements", callback_data='menu_achievements')
        ],
        [
            InlineKeyboardButton("ℹ️ Help / About", callback_data='menu_help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lessons_menu_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Lessons submenu with categories"""
    keyboard = []
    
    for cat in categories:
        emoji = cat.get('icon', '📖')
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {cat['name']}", 
                callback_data=f'cat_{cat['slug']}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_menu')])
    return InlineKeyboardMarkup(keyboard)

def get_lessons_list_keyboard(lessons: List[Dict[str, Any]], 
                               completed_ids: List[str] = None) -> InlineKeyboardMarkup:
    """List of lessons for a category"""
    if completed_ids is None:
        completed_ids = []
    
    keyboard = []
    for lesson in lessons:
        status = "✅" if lesson['id'] in completed_ids else "⭕"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {lesson['name']}",
                callback_data=f'lesson_{lesson['slug']}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_lessons')])
    return InlineKeyboardMarkup(keyboard)

def get_lesson_action_keyboard(lesson_slug: str, completed: bool = False) -> InlineKeyboardMarkup:
    """Actions available during a lesson"""
    keyboard = []
    
    if not completed:
        keyboard.append([
            InlineKeyboardButton("✅ Mark Complete", callback_data=f'complete_{lesson_slug}')
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("📝 Add to Vocab", callback_data=f'vocab_{lesson_slug}'),
            InlineKeyboardButton("🔁 Practice", callback_data=f'practice_{lesson_slug}')
        ],
        [
            InlineKeyboardButton("⬅️ Prev Lesson", callback_data=f'nav_prev_{lesson_slug}'),
            InlineKeyboardButton("Next Lesson ➡️", callback_data=f'nav_next_{lesson_slug}')
        ],
        [InlineKeyboardButton("🔙 Back to Lessons", callback_data='back_category')]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_practice_mode_keyboard() -> InlineKeyboardMarkup:
    """Practice mode options"""
    keyboard = [
        [
            InlineKeyboardButton("🗣️ Pronunciation", callback_data='practice_pronunciation'),
            InlineKeyboardButton("💬 Conversation", callback_data='practice_conversation')
        ],
        [
            InlineKeyboardButton("📝 Vocabulary", callback_data='practice_vocab'),
            InlineKeyboardButton("📖 Review", callback_data='practice_review')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_vocab_actions_keyboard(word_id: str, is_starred: bool = False) -> InlineKeyboardMarkup:
    """Actions for vocabulary items"""
    star_text = "⭐ Unstar" if is_starred else "☆ Star"
    
    keyboard = [
        [
            InlineKeyboardButton(star_text, callback_data=f'vocab_star_{word_id}'),
            InlineKeyboardButton("🔊 Hear Pronunciation", callback_data=f'vocab_audio_{word_id}')
        ],
        [InlineKeyboardButton("❌ Remove", callback_data=f'vocab_remove_{word_id}')],
        [InlineKeyboardButton("🔙 Back to Vocab", callback_data='back_vocab')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_progress_view_keyboard() -> InlineKeyboardMarkup:
    """Progress view options"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Stats", callback_data='progress_stats'),
            InlineKeyboardButton("📚 Lessons Done", callback_data='progress_lessons')
        ],
        [
            InlineKeyboardButton("🔥 Streak", callback_data='progress_streak'),
            InlineKeyboardButton("📅 Activity", callback_data='progress_activity')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_voice_prompt_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard encouraging voice use"""
    keyboard = [[KeyboardButton("🎤 Send Voice", request_contact=False)]]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        one_time_keyboard=False
    )

def get_help_keyboard() -> InlineKeyboardMarkup:
    """Help menu options"""
    keyboard = [
        [
            InlineKeyboardButton("📖 How to Use", callback_data='help_usage'),
            InlineKeyboardButton("🎤 Voice Tips", callback_data='help_voice')
        ],
        [
            InlineKeyboardButton("🇬🇭 About Twi", callback_data='help_about_twi'),
            InlineKeyboardButton("❓ FAQ", callback_data='help_faq')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_conversation_continue_keyboard() -> InlineKeyboardMarkup:
    """Continue or end conversation"""
    keyboard = [
        [
            InlineKeyboardButton("🗣️ Reply with Voice", callback_data='reply_voice'),
            InlineKeyboardButton("💬 Reply with Text", callback_data='reply_text')
        ],
        [
            InlineKeyboardButton("🎭 New Topic", callback_data='conv_new'),
            InlineKeyboardButton("📋 End Session", callback_data='conv_end')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
