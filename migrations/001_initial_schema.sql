-- Twi Tutor Bot Database Schema
-- Supabase PostgreSQL

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    native_language TEXT DEFAULT 'en',
    learning_level TEXT DEFAULT 'beginner', -- beginner, intermediate, advanced
    daily_goal_min INTEGER DEFAULT 15,
    preferred_voice_speed TEXT DEFAULT 'normal', -- slow, normal, fast
    streak_count INTEGER DEFAULT 0,
    last_streak_date DATE,
    timezone TEXT DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE
);

-- Categories table (lessons grouped by themes)
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_twi TEXT,
    description TEXT,
    description_twi TEXT,
    icon TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lessons table  
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_twi TEXT,
    description TEXT,
    description_twi TEXT,
    content JSONB NOT NULL, -- structured lesson content
    vocabulary JSONB NOT NULL, -- vocabulary items
    grammar_points JSONB,
    cultural_notes JSONB,
    difficulty TEXT DEFAULT 'beginner', -- beginner, intermediate, advanced
    estimated_minutes INTEGER DEFAULT 10,
    display_order INTEGER DEFAULT 0,
    prerequisites UUID[], -- array of lesson uuids
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User progress table (lesson completion tracking)
CREATE TABLE IF NOT EXISTS user_lesson_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'not_started', -- not_started, in_progress, completed
    completion_percentage INTEGER DEFAULT 0,
    score INTEGER,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    attempts_count INTEGER DEFAULT 0,
    time_spent_min INTEGER DEFAULT 0,
    notes TEXT,
    UNIQUE(user_id, lesson_id)
);

-- Daily activity log (for streaks and analytics)
CREATE TABLE IF NOT EXISTS user_daily_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE DEFAULT CURRENT_DATE,
    total_minutes INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    voice_messages_sent INTEGER DEFAULT 0,
    messages_exchanged INTEGER DEFAULT 0,
    UNIQUE(user_id, activity_date)
);

-- Conversation history (lessons + free practice)
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
    session_type TEXT DEFAULT 'free_practice', -- lesson, free_practice, review
    role TEXT NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    content_twi TEXT, -- Twi version if applicable
    voice_url TEXT,
    voice_duration_sec INTEGER,
    was_transcribed BOOLEAN DEFAULT FALSE,
    transcription_confidence FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User vocabulary deck (custom vocab tracking)
CREATE TABLE IF NOT EXISTS user_vocabulary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    word_twi TEXT NOT NULL,
    word_english TEXT NOT NULL,
    pronunciation TEXT,
    example_sentence_twi TEXT,
    example_sentence_english TEXT,
    lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
    source TEXT DEFAULT 'lesson', -- lesson, user_added, ai_suggested
    proficiency_level INTEGER DEFAULT 0, -- 0-5 spaced repetition level
    next_review_at TIMESTAMPTZ,
    review_count INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    is_starred BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_twi TEXT,
    description TEXT,
    icon TEXT,
    criteria JSONB NOT NULL, -- conditions to unlock
    points INTEGER DEFAULT 0
);

-- User achievements
CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- Sessions for activity tracking
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    session_type TEXT DEFAULT 'practice',
    total_messages INTEGER DEFAULT 0,
    voice_messages_received INTEGER DEFAULT 0,
    voice_messages_sent INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_categories_order ON categories(display_order);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons(category_id);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(display_order);
CREATE INDEX IF NOT EXISTS idx_lessons_difficulty ON lessons(difficulty);
CREATE INDEX IF NOT EXISTS idx_progress_user ON user_lesson_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_lesson ON user_lesson_progress(lesson_id);
CREATE INDEX IF NOT EXISTS idx_progress_status ON user_lesson_progress(status);
CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_lesson ON conversation_history(lesson_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_history(created_at);
CREATE INDEX IF NOT EXISTS idx_vocab_user ON user_vocabulary(user_id);
CREATE INDEX IF NOT EXISTS idx_vocab_next_review ON user_vocabulary(next_review_at);
CREATE INDEX IF NOT EXISTS idx_activity_user_date ON user_daily_activity(user_id, activity_date);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_lesson_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_daily_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_vocabulary ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see/modify their own data
CREATE POLICY user_own_data ON users
    FOR ALL TO authenticated
    USING (telegram_id = current_setting('app.current_user_id')::BIGINT)
    WITH CHECK (telegram_id = current_setting('app.current_user_id')::BIGINT);

-- Categories and lessons are public (readable)
CREATE POLICY categories_public ON categories
    FOR SELECT TO authenticated USING (is_active = TRUE);

CREATE POLICY lessons_public ON lessons  
    FOR SELECT TO authenticated USING (is_active = TRUE);

-- Progress is private per user
CREATE POLICY progress_user_own ON user_lesson_progress
    FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM users WHERE users.id = user_lesson_progress.user_id 
        AND users.telegram_id = current_setting('app.current_user_id')::BIGINT
    ));

-- Conversation history is private per user
CREATE POLICY conversation_user_own ON conversation_history
    FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM users WHERE users.id = conversation_history.user_id
        AND users.telegram_id = current_setting('app.current_user_id')::BIGINT
    ));

-- Vocabulary is private per user
CREATE POLICY vocabulary_user_own ON user_vocabulary
    FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM users WHERE users.id = user_vocabulary.user_id
        AND users.telegram_id = current_setting('app.current_user_id')::BIGINT
    ));

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to maintain streak count
CREATE OR REPLACE FUNCTION update_user_streak()
RETURNS TRIGGER AS $$
DECLARE
    last_activity DATE;
    gap_days INTEGER;
BEGIN
    -- Get last activity date
    SELECT MAX(activity_date) INTO last_activity
    FROM user_daily_activity
    WHERE user_id = NEW.user_id AND activity_date < NEW.activity_date;
    
    IF last_activity IS NULL THEN
        -- First activity
        UPDATE users 
        SET streak_count = 1, last_streak_date = NEW.activity_date, last_active_at = NOW()
        WHERE id = NEW.user_id;
    ELSE
        gap_days = NEW.activity_date - last_activity;
        IF gap_days = 1 THEN
            -- Continuing streak
            UPDATE users 
            SET streak_count = streak_count + 1, last_streak_date = NEW.activity_date, last_active_at = NOW()
            WHERE id = NEW.user_id;
        ELSIF gap_days > 1 THEN
            -- Streak broken, reset
            UPDATE users 
            SET streak_count = 1, last_streak_date = NEW.activity_date, last_active_at = NOW()
            WHERE id = NEW.user_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_streak
    AFTER INSERT ON user_daily_activity
    FOR EACH ROW EXECUTE FUNCTION update_user_streak();

-- Storage bucket for audio files
INSERT INTO storage.buckets (id, name, public)
VALUES ('audio-responses', 'Audio bot responses', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policy for audio
CREATE POLICY audio_responses_policy ON storage.objects
    FOR ALL TO authenticated
    USING (bucket_id = 'audio-responses')
    WITH CHECK (bucket_id = 'audio-responses');
