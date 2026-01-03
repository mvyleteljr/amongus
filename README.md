# LLM Among Us

A game where 4 LLMs compete in programming tasks. One is secretly an imposter trying to sabotage. The others must identify the imposter while collaboratively solving tasks.

## Setup

### Backend

```bash
cd backend
uv sync
```

Set your API keys for all providers:
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

Run the server:
```bash
uv run python main.py
```

The backend runs at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at http://localhost:5173

## How to Play

1. Open the frontend in your browser
2. Click "Create Game" to set up a new game
3. Click "Start Game" to begin
4. Click "Advance" buttons to progress through each phase:
   - **Coding**: LLMs write solutions to programming tasks
   - **Reveal**: All code is shown to all players
   - **Discussion**: 3 rounds of discussion about the code
   - **Voting**: LLMs vote on which solution to use and who they suspect
   - **Results**: The chosen solution is tested

## Win Conditions

- **Crewmates win**: If the imposter is voted out (majority vote)
- **Imposter wins**: If the imposter survives all 5 rounds OR 3+ tasks fail

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **LLM Providers**: Claude (Anthropic), GPT-4o (OpenAI), Gemini (Google), DeepSeek
