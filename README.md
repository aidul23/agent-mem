# GPT-Lab Agent with Hindsight Memory

A LangChain-based agent that uses Hindsight as long-term memory with explicit user consent for data storage.

## Features

- **LangChain Integration**: Uses LangChain for agent orchestration
- **Hindsight Memory**: Long-term memory storage via Hindsight
- **Explicit Consent**: Only stores user data after explicit consent
- **Web Demo**: Beautiful, modern web interface for testing

## Prerequisites

- Python 3.8+
- Docker (for running Hindsight server)
- OpenAI API key

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# 3. Start Hindsight (in one terminal)
docker-compose up -d

# 4. Start the web app (in another terminal)
./start.sh
# or: python app.py

# 5. Open http://localhost:5000 in your browser
```

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Or export it:

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Start Hindsight Server

**Option A: Using Docker Compose (recommended)**

```bash
docker-compose up -d
```

**Option B: Using Docker directly**

```bash
docker run --rm -it --pull always -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY=$OPENAI_API_KEY \
  -e HINDSIGHT_API_LLM_MODEL=gpt-4o-mini \
  -v $HOME/.hindsight-docker:/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:latest
```

This will:
- Start Hindsight API at `http://localhost:8888`
- Use GPT-4o-mini for memory operations
- Persist data in `~/.hindsight-docker` (or Docker volume with docker-compose)

### 4. Start the Flask Application

**Option A: Using the startup script (recommended)**

```bash
./start.sh
```

**Option B: Manual start**

In a new terminal:

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

## Usage

1. Open `http://localhost:5000` in your browser
2. Choose whether to allow memory storage (consent is required)
3. Start chatting with the agent
4. The agent will recall relevant memories and store new interactions (if consent was given)

## Architecture

### Components

- **`memory_layer.py`**: Wrapper around Hindsight client for memory operations
- **`auth_and_profile.py`**: User consent management (in-memory for demo)
- **`agent.py`**: LangChain agent that integrates Hindsight memory
- **`app.py`**: Flask web server with REST API
- **`static/index.html`**: Frontend web interface

### Memory Flow

1. User sends a message
2. Agent recalls relevant memories from Hindsight (if consent given)
3. Memories are injected into the system prompt
4. Agent generates response using LangChain
5. Interaction is stored in Hindsight (if consent given)

### Consent Model

- Users must explicitly consent before data storage
- Consent is stored per user ID
- Memory operations are skipped if consent is not given
- Agent remains fully functional without memory

## Development

### Project Structure

```
agent-mem/
├── app.py                 # Flask web server
├── agent.py               # LangChain agent with Hindsight
├── auth_and_profile.py    # User consent management
├── memory_layer.py        # Hindsight memory wrapper
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── static/
    └── index.html        # Web frontend
```

### Customization

- **Model**: Change the model in `agent.py` (currently `gpt-4o-mini`)
- **Memory Bank**: Each user gets a unique bank ID: `user-{user_id}`
- **Storage**: Replace in-memory `USER_DB` in `auth_and_profile.py` with a real database
- **UI**: Customize `static/index.html` for your needs

## Notes

- This is a demo implementation. For production:
  - Use a proper database for user profiles
  - Add authentication/authorization
  - Add error handling and logging
  - Consider rate limiting
  - Add input validation and sanitization

## References

- [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- [Hindsight Python SDK](https://hindsight.vectorize.io/sdks/python)
- [LangChain Documentation](https://docs.langchain.com)

