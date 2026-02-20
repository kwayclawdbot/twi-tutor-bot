#!/bin/bash
echo "🔧 Twi Tutor Bot Setup"
echo "======================"

# Check Python version
PYV=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQ="3.9"
if [ "$(printf '%s\n' "$REQ" "$PYV" | sort -V | head -n1)" != "$REQ" ]; then
    echo "❌ Python $REQ+ required. Found $PYV"
    exit 1
fi

echo "✅ Python $PYV detected"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup .env
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your tokens"
echo "2. Setup Supabase (local or cloud)"
echo "3. Run: python src/bot.py"
echo ""
echo "🌍 Akwaaba!"
