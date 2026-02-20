"""
Twi Tutor Bot - Database Seeding Script
Populates Supabase with curriculum data from curriculum.json
"""
import json
import asyncio
import logging
from pathlib import Path

from src.database import db
from src.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_database():
    """Seed database with curriculum data"""
    
    # Load curriculum
    curriculum_path = config.CURRICULUM_PATH
    
    if not curriculum_path.exists():
        logger.error(f"Curriculum file not found: {curriculum_path}")
        return
    
    with open(curriculum_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    curriculum = data['curriculum']
    
    logger.info("🌱 Seeding database with curriculum data...")
    
    # Seed categories and lessons
    categories = curriculum.get('categories', [])
    
    for cat_data in categories:
        # Check if category exists
        existing = db.client.table('categories')\
            .select('id')\
            .eq('slug', cat_data['slug'])\
            .execute()
        
        if existing.data:
            logger.info(f"Category '{cat_data['slug']}' already exists, skipping...")
            category_id = existing.data[0]['id']
        else:
            # Insert category
            cat_record = {
                'slug': cat_data['slug'],
                'name': cat_data['name'],
                'name_twi': cat_data.get('name_twi', ''),
                'description': cat_data.get('description', ''),
                'description_twi': cat_data.get('description_twi', ''),
                'icon': cat_data.get('icon', '📖'),
                'display_order': cat_data.get('display_order', 0)
            }
            
            result = db.client.table('categories').insert(cat_record).execute()
            category_id = result.data[0]['id']
            logger.info(f"✅ Created category: {cat_data['name']}")
        
        # Seed lessons for this category
        lessons = cat_data.get('lessons', [])
        
        for lesson_data in lessons:
            # Check if lesson exists
            existing_lesson = db.client.table('lessons')\
                .select('id')\
                .eq('slug', lesson_data['slug'])\
                .execute()
            
            if existing_lesson.data:
                logger.info(f"  Lesson '{lesson_data['slug']}' already exists, skipping...")
                continue
            
            # Prepare lesson record
            lesson_record = {
                'category_id': category_id,
                'slug': lesson_data['slug'],
                'name': lesson_data['name'],
                'name_twi': lesson_data.get('name_twi', ''),
                'description': lesson_data.get('description', ''),
                'description_twi': lesson_data.get('description_twi', ''),
                'content': lesson_data.get('content', {}),
                'vocabulary': lesson_data.get('vocabulary', []),
                'grammar_points': lesson_data.get('grammar_points', []),
                'cultural_notes': lesson_data.get('cultural_notes', ''),
                'difficulty': lesson_data.get('difficulty', 'beginner'),
                'estimated_minutes': lesson_data.get('estimated_minutes', 10),
                'display_order': lesson_data.get('display_order', 0)
            }
            
            db.client.table('lessons').insert(lesson_record).execute()
            logger.info(f"  ✅ Created lesson: {lesson_data['name']}")
    
    # Seed achievements
    achievements = curriculum.get('achievements', [])
    
    for ach_data in achievements:
        existing_ach = db.client.table('achievements')\
            .select('id')\
            .eq('slug', ach_data['slug'])\
            .execute()
        
        if existing_ach.data:
            logger.info(f"Achievement '{ach_data['slug']}' already exists, skipping...")
            continue
        
        ach_record = {
            'slug': ach_data['slug'],
            'name': ach_data['name'],
            'name_twi': ach_data.get('name_twi', ''),
            'description': ach_data.get('description', ''),
            'criteria': {},  # To be defined
            'points': ach_data.get('points', 10)
        }
        
        db.client.table('achievements').insert(ach_record).execute()
        logger.info(f"🏆 Created achievement: {ach_data['name']}")
    
    logger.info("\n✨ Database seeding complete!")
    logger.info(f"📚 Categories: {len(categories)}")
    logger.info(f"📝 Total lessons: {sum(len(c['lessons']) for c in categories)}")
    logger.info(f"🏆 Achievements: {len(achievements)}")

if __name__ == '__main__':
    asyncio.run(seed_database())
