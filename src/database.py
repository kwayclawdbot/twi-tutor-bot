"""
Twi Tutor Bot - Database Module
Supabase integration for user data, lessons, progress, and conversation history.
"""
import json
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from supabase import create_client, Client
from postgrest.exceptions import APIError

from src.config import config

logger = logging.getLogger(__name__)

class Database:
    """Supabase database operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Initialize Supabase connection"""
        try:
            self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("✅ Connected to Supabase")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            raise
    
    # ==================== USER OPERATIONS ====================
    
    async def get_or_create_user(self, telegram_id: int, 
                                  username: Optional[str] = None,
                                  first_name: Optional[str] = None,
                                  last_name: Optional[str] = None) -> Dict[str, Any]:
        """Get existing user or create new one"""
        try:
            # Try to get existing user
            result = self.client.table('users')\
                .select('*')\
                .eq('telegram_id', telegram_id)\
                .single()\
                .execute()
            
            if result.data:
                # Update last active
                self.client.table('users')\
                    .update({'last_active_at': datetime.utcnow().isoformat()})\
                    .eq('id', result.data['id'])\
                    .execute()
                logger.info(f"👤 Retrieved user: {telegram_id}")
                return result.data
            
            # Create new user
            new_user = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('users')\
                .insert(new_user)\
                .execute()
            
            logger.info(f"🆕 Created new user: {telegram_id}")
            
            # Initialize daily activity for today
            await self.log_daily_activity(result.data[0]['id'], activity_date=date.today())
            
            return result.data[0]
            
        except APIError as e:
            # Handle case where single() returns no rows
            if 'JSON object requested' in str(e):
                # Create new user
                new_user = {
                    'telegram_id': telegram_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'created_at': datetime.utcnow().isoformat()
                }
                result = self.client.table('users').insert(new_user).execute()
                logger.info(f"🆕 Created new user: {telegram_id}")
                return result.data[0]
            logger.error(f"Database error in get_or_create_user: {e}")
            raise
    
    async def update_user_level(self, user_id: UUID, level: str):
        """Update user's learning level"""
        try:
            self.client.table('users')\
                .update({'learning_level': level})\
                .eq('id', str(user_id))\
                .execute()
        except Exception as e:
            logger.error(f"Error updating user level: {e}")
    
    async def get_user_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            # Get user base data
            user_result = self.client.table('users')\
                .select('streak_count, learning_level, created_at, last_active_at')\
                .eq('id', str(user_id))\
                .single()\
                .execute()
            
            # Get lessons completed
            progress_result = self.client.table('user_lesson_progress')\
                .select('status')\
                .eq('user_id', str(user_id))\
                .eq('status', 'completed')\
                .execute()
            
            # Get total practice time
            activity_result = self.client.table('user_daily_activity')\
                .select('total_minutes')\
                .eq('user_id', str(user_id))\
                .execute()
            
            total_minutes = sum(day['total_minutes'] for day in activity_result.data)
            
            return {
                'streak': user_result.data.get('streak_count', 0),
                'level': user_result.data.get('learning_level', 'beginner'),
                'lessons_completed': len(progress_result.data),
                'total_minutes': total_minutes,
                'member_since': user_result.data.get('created_at')
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {'streak': 0, 'level': 'beginner', 'lessons_completed': 0, 'total_minutes': 0}
    
    # ==================== LESSON OPERATIONS ====================
    
    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all lesson categories"""
        try:
            result = self.client.table('categories')\
                .select('*')\
                .eq('is_active', True)\
                .order('display_order')\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    async def get_lessons_by_category(self, category_slug: str) -> List[Dict[str, Any]]:
        """Get lessons for a specific category"""
        try:
            # First get category id
            cat_result = self.client.table('categories')\
                .select('id')\
                .eq('slug', category_slug)\
                .single()\
                .execute()
            
            if not cat_result.data:
                return []
            
            # Get lessons
            result = self.client.table('lessons')\
                .select('*')\
                .eq('category_id', cat_result.data['id'])\
                .eq('is_active', True)\
                .order('display_order')\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching lessons: {e}")
            return []
    
    async def get_lesson_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get a specific lesson by slug"""
        try:
            result = self.client.table('lessons')\
                .select('*, categories!inner(name, slug)')\
                .eq('slug', slug)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching lesson {slug}: {e}")
            return None
    
    async def get_recommended_lesson(self, user_id: UUID, level: str) -> Optional[Dict[str, Any]]:
        """Get next recommended lesson for user"""
        try:
            # Get completed lessons
            completed = self.client.table('user_lesson_progress')\
                .select('lesson_id')\
                .eq('user_id', str(user_id))\
                .eq('status', 'completed')\
                .execute()
            
            completed_ids = [c['lesson_id'] for c in completed.data]
            
            # Get lessons matching user level, not completed
            result = self.client.table('lessons')\
                .select('*')\
                .eq('difficulty', level)\
                .eq('is_active', True)\
                .order('display_order')\
                .execute()
            
            # Find first uncompleted lesson
            for lesson in result.data:
                if lesson['id'] not in completed_ids:
                    return lesson
            
            # If all completed at this level, return first of next level
            if level == 'beginner':
                next_level = 'intermediate'
            elif level == 'intermediate':
                next_level = 'advanced'
            else:
                return result.data[0] if result.data else None
                
            result = self.client.table('lessons')\
                .select('*')\
                .eq('difficulty', next_level)\
                .eq('is_active', True)\
                .order('display_order')\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error getting recommended lesson: {e}")
            return None
    
    # ==================== PROGRESS OPERATIONS ====================
    
    async def get_or_create_progress(self, user_id: UUID, lesson_id: UUID) -> Dict[str, Any]:
        """Get or create lesson progress"""
        try:
            result = self.client.table('user_lesson_progress')\
                .select('*')\
                .eq('user_id', str(user_id))\
                .eq('lesson_id', str(lesson_id))\
                .execute()
            
            if result.data:
                return result.data[0]
            
            # Create new progress
            new_progress = {
                'user_id': str(user_id),
                'lesson_id': str(lesson_id),
                'status': 'not_started',
                'started_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('user_lesson_progress')\
                .insert(new_progress)\
                .execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error in get_or_create_progress: {e}")
            raise
    
    async def update_progress(self, progress_id: UUID, updates: Dict[str, Any]):
        """Update lesson progress"""
        try:
            self.client.table('user_lesson_progress')\
                .update(updates)\
                .eq('id', str(progress_id))\
                .execute()
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
    
    async def complete_lesson(self, user_id: UUID, lesson_id: UUID, score: Optional[int] = None):
        """Mark lesson as completed"""
        try:
            updates = {
                'status': 'completed',
                'completion_percentage': 100,
                'completed_at': datetime.utcnow().isoformat()
            }
            if score:
                updates['score'] = score
            
            self.client.table('user_lesson_progress')\
                .update(updates)\
                .eq('user_id', str(user_id))\
                .eq('lesson_id', str(lesson_id))\
                .execute()
                
            logger.info(f"✅ Lesson {lesson_id} completed by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error completing lesson: {e}")
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    async def save_message(self, user_id: UUID, role: str, content: str,
                          content_twi: Optional[str] = None,
                          lesson_id: Optional[UUID] = None,
                          voice_url: Optional[str] = None,
                          voice_duration: Optional[int] = None,
                          was_transcribed: bool = False,
                          metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Save a conversation message"""
        try:
            message = {
                'user_id': str(user_id),
                'role': role,
                'content': content,
                'content_twi': content_twi,
                'lesson_id': str(lesson_id) if lesson_id else None,
                'voice_url': voice_url,
                'voice_duration_sec': voice_duration,
                'was_transcribed': was_transcribed,
                'metadata': metadata or {}
            }
            
            result = self.client.table('conversation_history')\
                .insert(message)\
                .execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    async def get_conversation_history(self, user_id: UUID, 
                                        limit: int = 20,
                                        lesson_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        try:
            query = self.client.table('conversation_history')\
                .select('*')\
                .eq('user_id', str(user_id))\
                .order('created_at', desc=True)\
                .limit(limit)
            
            if lesson_id:
                query = query.eq('lesson_id', str(lesson_id))
            
            result = query.execute()
            
            # Return in chronological order
            return list(reversed(result.data))
            
        except Exception as e:
            logger.error(f"Error fetching conversation history: {e}")
            return []
    
    # ==================== ACTIVITY TRACKING ====================
    
    async def log_daily_activity(self, user_id: UUID, 
                                  activity_date: date = None,
                                  minutes: int = 0,
                                  voice_sent: bool = False,
                                  message_count: int = 1):
        """Log daily user activity"""
        try:
            if activity_date is None:
                activity_date = date.today()
            
            # Try to update existing record
            existing = self.client.table('user_daily_activity')\
                .select('*')\
                .eq('user_id', str(user_id))\
                .eq('activity_date', activity_date.isoformat())\
                .execute()
            
            if existing.data:
                # Update
                updates = {
                    'total_minutes': existing.data[0]['total_minutes'] + minutes,
                    'messages_exchanged': existing.data[0]['messages_exchanged'] + message_count
                }
                if voice_sent:
                    updates['voice_messages_sent'] = existing.data[0]['voice_messages_sent'] + 1
                
                self.client.table('user_daily_activity')\
                    .update(updates)\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
            else:
                # Create new
                new_activity = {
                    'user_id': str(user_id),
                    'activity_date': activity_date.isoformat(),
                    'total_minutes': minutes,
                    'messages_exchanged': message_count,
                    'voice_messages_sent': 1 if voice_sent else 0
                }
                self.client.table('user_daily_activity')\
                    .insert(new_activity)\
                    .execute()
                    
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    # ==================== VOCABULARY OPERATIONS ====================
    
    async def add_vocabulary(self, user_id: UUID, word_twi: str, word_english: str,
                             pronunciation: Optional[str] = None,
                             example_twi: Optional[str] = None,
                             example_english: Optional[str] = None,
                             source: str = 'lesson') -> Dict[str, Any]:
        """Add word to user's vocabulary deck"""
        try:
            vocab = {
                'user_id': str(user_id),
                'word_twi': word_twi,
                'word_english': word_english,
                'pronunciation': pronunciation,
                'example_sentence_twi': example_twi,
                'example_sentence_english': example_english,
                'source': source
            }
            
            result = self.client.table('user_vocabulary')\
                .insert(vocab)\
                .execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error adding vocabulary: {e}")
            raise
    
    async def get_user_vocabulary(self, user_id: UUID, 
                                   limit: int = 20,
                                   starred_only: bool = False) -> List[Dict[str, Any]]:
        """Get user's vocabulary list"""
        try:
            query = self.client.table('user_vocabulary')\
                .select('*')\
                .eq('user_id', str(user_id))\
                .order('created_at', desc=True)\
                .limit(limit)
            
            if starred_only:
                query = query.eq('is_starred', True)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error fetching vocabulary: {e}")
            return []

# Singleton instance
db = Database()
