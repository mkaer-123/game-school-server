#!/bin/bash
# Setup script for Game Server

echo "🎮 Game Server Setup"
echo "===================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not installed. Download from https://ollama.ai"
    echo "   After installing, run: ollama pull mistral"
else
    echo "✅ Ollama found"
fi

# Install dependencies
echo ""
echo "📦 Installing Python packages..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. In another terminal, run: python server.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
