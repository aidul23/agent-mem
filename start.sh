#!/bin/bash

# Start script for GPT-Lab Agent with Hindsight Memory

echo "🚀 Starting GPT-Lab Agent with Hindsight Memory"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please create a .env file with your OPENAI_API_KEY"
    echo "   Example: echo 'OPENAI_API_KEY=your-key' > .env"
    echo ""
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    echo "   Please set it in .env file or export it:"
    echo "   export OPENAI_API_KEY=your-key"
    exit 1
fi

echo "✅ OpenAI API key found"
echo ""

# Check if Hindsight is running
if ! curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Hindsight server not responding at http://localhost:8888"
    echo "   Please start Hindsight first:"
    echo "   docker run --rm -it --pull always -p 8888:8888 -p 9999:9999 \\"
    echo "     -e HINDSIGHT_API_LLM_API_KEY=\$OPENAI_API_KEY \\"
    echo "     -e HINDSIGHT_API_LLM_MODEL=gpt-4o-mini \\"
    echo "     -v \$HOME/.hindsight-docker:/home/hindsight/.pg0 \\"
    echo "     ghcr.io/vectorize-io/hindsight:latest"
    echo ""
    echo "   Or use docker-compose:"
    echo "   docker-compose up -d"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Starting Flask application..."
echo "   Web interface: http://localhost:5001"
echo ""

python app.py

