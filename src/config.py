"""
Twi Tutor Bot - Configuration Module
"""
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

@dataclass
class Config:
    """Application configuration"""
    # Telegram
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', '')
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    WHISPER_MODEL: str = 'whisper-1'
    GPT_MODEL: str = 'gpt-4o'
    TTS_MODEL: str = 'tts-1'
    TTS_VOICE: str = 'nova'  # Warm, friendly voice
    
    # Supabase
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', 'http://127.0.0.1:54321')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    
    # Bot Configuration
    MAX_VOICE_DURATION: int = 60  # seconds
    MAX_TEXT_LENGTH: int = 4000
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Audio Storage
    AUDIO_STORAGE_PATH: Path = Path(__file__).parent.parent / 'data' / 'audio'
    
    # Data Files
    CURRICULUM_PATH: Path = Path(__file__).parent.parent / 'data' / 'curriculum.json'
    
    def __post_init__(self):
        # Ensure audio directory exists
        self.AUDIO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

config = Config()
