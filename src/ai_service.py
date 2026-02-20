"""
Twi Tutor Bot - AI Services Module
OpenAI integration for Whisper (STT), GPT-4 (chat), and TTS (voice generation)
"""
import os
import logging
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from openai import AsyncOpenAI

from src.config import config
from src.database import db

logger = logging.getLogger(__name__)

class AIService:
    """OpenAI API services for the bot"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    
    # ==================== SPEECH TO TEXT ====================
    
    async def transcribe_voice(self, voice_file_path: str) -> Tuple[str, float]:
        """
        Transcribe voice message to text using Whisper
        
        Returns:
            Tuple of (transcription_text, confidence_score)
        """
        try:
            with open(voice_file_path, 'rb') as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=config.WHISPER_MODEL,
                    file=audio_file,
                    language="tw"  # ISO code for Twi/Akan (may fall back to related languages)
                )
            
            transcription = response.text
            # Whisper doesn't return confidence directly, estimate based on response quality
            confidence = 0.9 if transcription and len(transcription) > 3 else 0.5
            
            logger.info(f"🎤 Transcribed: {transcription[:50]}...")
            return transcription, confidence
            
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")
            return "", 0.0
    
    # ==================== CHAT / LESSON GENERATION ====================
    
    async def generate_response(self, 
                                 messages: List[Dict[str, str]], 
                                 system_prompt: Optional[str] = None,
                                 temperature: float = 0.7) -> str:
        """
        Generate AI response using GPT-4
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt override
            temperature: Creativity level (0.0-1.0)
            
        Returns:
            Generated text response
        """
        try:
            # Build message array
            full_messages = []
            
            if system_prompt:
                full_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            full_messages.extend(messages)
            
            response = await self.client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=full_messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            logger.info(f"🤖 AI generated response: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI generation error: {e}")
            return "Me kronrono... (I'm sorry...)\n\nI seem to be having trouble thinking right now. Let's try again in a moment!"
    
    async def generate_lesson_content(self, lesson_data: Dict[str, Any], 
                                       user_level: str) -> str:
        """Generate personalized lesson content"""
        try:
            vocab_list = lesson_data.get('vocabulary', [])
            vocab_formatted = "\n".join([
                f"- {item.get('word', '')}: {item.get('meaning', '')} ({item.get('pronunciation', '')})"
                for item in vocab_list
            ])
            
            cultural_note = lesson_data.get('cultural_notes', '')
            
            prompt = f"""
You are Nana Akosua, a warm Ghanaian elder teaching Twi. Create an engaging lesson introduction.

LESSON: {lesson_data.get('name', '')} ({lesson_data.get('name_twi', '')})
LEVEL: {user_level}

VOCABULARY TO COVER:
{vocab_formatted}

CULTURAL CONTEXT:
{cultural_note}

RESPOND IN THIS FORMAT:
[TWI GREETING AND INTRO]

[ENGLISH TRANSLATION]

[CULTURAL STORY]

Be warm, encouraging, and mention 2-3 vocabulary words with pronunciation tips.
"""
            
            response = await self.client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Lesson generation error: {e}")
            return "Akwaaba! Let's begin this wonderful lesson together. 🌟"
    
    async def check_pronunciation(self, spoken_text: str, 
                                   expected_text: str) -> Dict[str, Any]:
        """Check pronunciation and provide feedback"""
        try:
            prompt = f"""
You are a gentle Twi pronunciation coach. Compare what the student said vs. what was expected.

STUDENT SAID: {spoken_text}
EXPECTED: {expected_text}

Provide:
1. A gentle assessment (don't be harsh!)
2. Specific pronunciation tips for any tricky sounds
3. Encouragement to try again

Format: Brief Twi feedback, then English translation.
"""
            
            response = await self.client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=300
            )
            
            return {
                'feedback': response.choices[0].message.content,
                'match_confidence': self._estimate_match(spoken_text, expected_text)
            }
            
        except Exception as e:
            logger.error(f"❌ Pronunciation check error: {e}")
            return {'feedback': 'Ayɛ paa! Good try!', 'match_confidence': 0.7}
    
    def _estimate_match(self, spoken: str, expected: str) -> float:
        """Simple string similarity for pronunciation confidence"""
        spoken_clean = spoken.lower().strip()
        expected_clean = expected.lower().strip()
        
        if spoken_clean == expected_clean:
            return 1.0
        
        # Calculate similarity ratio
        from difflib import SequenceMatcher
        return SequenceMatcher(None, spoken_clean, expected_clean).ratio()
    
    # ==================== TEXT TO SPEECH ====================
    
    async def generate_voice(self, text: str) -> Optional[str]:
        """
        Generate voice response using OpenAI TTS
        
        Args:
            text: Text to speak (should be Twi portion only)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            # Clean text - extract just Twi portion if formatted response
            if '[TWI' in text.upper() or '[ENGLISH' in text.upper():
                # Extract Twi section
                twi_section = self._extract_section(text, '[TWI', '[ENGLISH')
                if twi_section:
                    text = twi_section
            
            # Truncate if too long (TTS has limits)
            if len(text) > 4000:
                text = text[:4000]
            
            # Generate audio
            response = await self.client.audio.speech.create(
                model=config.TTS_MODEL,
                voice=config.TTS_VOICE,  # Nova is warm and friendly
                input=text
            )
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', 
                                              dir=config.AUDIO_STORAGE_PATH) as tmp_file:
                response.stream_to_file(tmp_file.name)
                audio_path = tmp_file.name
            
            logger.info(f"🔊 Generated voice: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ TTS generation error: {e}")
            return None
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> Optional[str]:
        """Extract content between markers"""
        start_idx = text.upper().find(start_marker.upper())
        if start_idx == -1:
            return None
        
        # Find the actual content start (after the marker line)
        content_start = text.find('\n', start_idx)
        if content_start == -1:
            content_start = start_idx + len(start_marker)
        else:
            content_start += 1
        
        # Find end marker
        end_idx = text.upper().find(end_marker.upper(), content_start)
        if end_idx == -1:
            return text[content_start:].strip()
        
        return text[content_start:end_idx].strip()

# Singleton instance
ai_service = AIService()
