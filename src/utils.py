"""
Twi Tutor Bot - Utility Functions
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import config

logger = logging.getLogger(__name__)


def load_curriculum() -> Dict[str, Any]:
    """Load curriculum from JSON file"""
    try:
        with open(config.CURRICULUM_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading curriculum: {e}")
        return {"categories": [], "lessons": []}


def format_lesson_content(lesson: Dict[str, Any]) -> str:
    """Format lesson content for display"""
    text = f"📖 **{lesson.get('name', 'Lesson')}**\n\n"
    
    if lesson.get('content', {}).get('overview'):
        overview = lesson['content']['overview']
        if isinstance(overview, dict):
            text += f"_{overview.get('twi', '')}_\n\n"
            text += f"{overview.get('english', '')}\n\n"
    
    if lesson.get('vocabulary'):
        text += "**Vocabulary:**\n"
        for item in lesson['vocabulary'][:5]:
            word = item.get('word', '')
            meaning = item.get('meaning', '')
            pronun = item.get('pronunciation', '')
            text += f"• {word} - {meaning}"
            if pronun:
                text += f" (_{pronun}_)"
            text += "\n"
    
    return text


def extract_twi_from_response(response: str) -> str:
    """Extract Twi portion from formatted response"""
    lines = response.split('\n')
    twi_lines = []
    in_twi_section = False
    
    for line in lines:
        if '[TWI' in line.upper() or 'TWI RESPONSE' in line.upper():
            in_twi_section = True
            continue
        elif '[ENGLISH' in line.upper() or 'ENGLISH TRANSLATION' in line.upper():
            in_twi_section = False
            continue
        
        if in_twi_section and line.strip():
            twi_lines.append(line)
    
    if twi_lines:
        return '\n'.join(twi_lines)
    
    # Fallback: return first paragraph
    return lines[0] if lines else response[:200]


def extract_english_from_response(response: str) -> str:
    """Extract English portion from formatted response"""
    lines = response.split('\n')
    english_lines = []
    in_english_section = False
    
    for line in lines:
        if '[ENGLISH' in line.upper() or 'ENGLISH TRANSLATION' in line.upper():
            in_english_section = True
            continue
        elif '[CULTURAL' in line.upper() or 'CULTURAL NOTE' in line.upper():
            in_english_section = False
            continue
        
        if in_english_section and line.strip():
            english_lines.append(line)
    
    return '\n'.join(english_lines) if english_lines else ""


def calculate_streak(last_date: Optional[str]) -> int:
    """Calculate streak based on last activity date"""
    from datetime import datetime, date
    
    if not last_date:
        return 0
    
    try:
        last = datetime.fromisoformat(last_date).date()
        today = date.today()
        diff = (today - last).days
        
        if diff == 0:
            return 1  # Active today
        elif diff == 1:
            return 1  # Continue tomorrow
        else:
            return 0  # Streak broken
    except:
        return 0


def sanitize_filename(filename: str) -> str:
    """Sanitize string for use as filename"""
    import re
    return re.sub(r'[^\w\-_.]', '_', filename)
