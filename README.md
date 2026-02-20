# Twi Tutor Bot

🌍 **Learn Twi with AI - Voice-First Language Tutoring**

A Telegram bot that teaches the Twi (Akan) language through voice conversations, structured lessons, and cultural storytelling.

## Features

- 🎤 **Voice-First**: Send voice messages, get voice responses with text
- 📚 **Structured Curriculum**: Lessons from basics to advanced
- 🧠 **AI Tutor**: Nana Akosua - warm Ghanaian elder persona
- 📊 **Progress Tracking**: Streaks, lessons completed, vocabulary
- 🌍 **Cultural Context**: Stories, proverbs, and Ghanaian customs
- 🔊 **OpenAI TTS**: Natural voice responses
- 🗣️ **Whisper STT**: Speech-to-text for pronunciation practice

## Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token (@BotFather)
- OpenAI API Key
- Supabase account (or local Supabase)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/twi-tutor-bot.git
cd twi-tutor-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your tokens

# Setup database (see Database Setup below)

# Run the bot
python src/bot.py
```

### Database Setup

1. **Option A: Local Supabase**
   ```bash
   npx supabase start
   # Run migrations:
   psql postgresql://postgres:postgres@127.0.0.1:54322/postgres -f migrations/001_initial_schema.sql
   ```

2. **Option B: Cloud Supabase**
   - Create project at supabase.com
   - Run SQL from `migrations/001_initial_schema.sql` in SQL Editor
   - Copy credentials to `.env`

## Project Structure

```
twi-tutor-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot handlers
│   ├── config.py           # Configuration
│   ├── database.py         # Supabase operations
│   ├── ai_service.py       # OpenAI integration
│   └── keyboards.py        # Telegram keyboards
├── data/
│   └── curriculum.json     # Twi lessons
├── migrations/
│   └── 001_initial_schema.sql
├── prompts/
│   └── tutor_persona.md    # AI personality
├── .env.example
├── requirements.txt
└── README.md
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & main menu |
| `/lesson` | Browse lesson categories |
| `/progress` | View stats & streaks |
| `/practice` | Free conversation mode |
| `/vocab` | Your saved words |
| `/help` | Help & FAQ |

## Curriculum

8 categorized lesson groups:
1. **Foundations** - Greetings, numbers, introductions
2. **Family** - Family relationships & titles
3. **Daily Life** - routines & time expressions
4. **Food** - Traditional foods & dining
5. **Travel** - Directions & transportation
6. **Culture** - Proverbs & traditions
7. **Conversation** - Small talk & questions

## AI Personality

Nana Akosua embodies:
- Warmth & patience of a Ghanaian elder
- Storytelling through cultural anecdotes
- Encouraging feedback on pronunciation
- Twi-first responses with English translations

## Tech Stack

- **Python** 3.9+
- **python-telegram-bot** - Telegram API
- **OpenAI** - Whisper, GPT-4, TTS
- **Supabase** - PostgreSQL backend
- **Supabase-py** - Python client

## Environment Variables

```bash
TELEGRAM_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=your_supabase_key
```

## Development

```bash
# Run with hot reload (install nodemon or similar)
nodemon --exec python src/bot.py

# Run tests
pytest tests/

# Type checking
mypy src/

# Linting
flake8 src/
black src/
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/bot.py"]
```

### Railway / Render / Heroku

1. Set environment variables
2. Deploy from GitHub
3. Ensure Supabase is accessible

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/xyz`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/xyz`)
5. Open Pull Request

## License

MIT License - see LICENSE file

## Acknowledgments

- Ghanaian linguistic resources & native speakers
- python-telegram-bot community
- OpenAI for Whisper, GPT-4, and TTS

---

**Akwaaba!** Start your Twi journey today 🇬🇭
