# EditScribe Backend

AI-powered professional manuscript editing platform.

## Features

- **Series Bible Manager**: Extracts characters, locations, timeline, objects
- **4-Stage Review**: Developmental, Line, Copy, Proofreading
- **Multi-LLM**: Claude Sonnet 4.5 + Gemini 2.5 Flash
- **Selective Editing**: Fix only what you want

## Setup

1. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the server:**
```bash
uvicorn api.main:app --reload
```

Server will be at: http://localhost:8000

## API Endpoints

- `POST /upload` - Upload manuscript
- `POST /bible/extract` - Extract Series Bible
- `GET /bible/{manuscript_id}` - Get Series Bible
- `PUT /bible/{manuscript_id}` - Update Series Bible
- `POST /review` - Run review agents
- `POST /edit` - Apply selected fixes
- `GET /export/{manuscript_id}` - Download edited manuscript

## Project Structure

```
backend/
├── agents/          # Review and editing agents
├── api/             # FastAPI routes
├── core/            # LLM client, document parser
└── tests/           # Unit tests
```

## LLM Strategy

**Claude Sonnet 4.5** (Premium):
- Series Bible Manager
- Developmental Review
- Prose Quality
- Selective Editor

**Gemini 2.5 Flash** (Budget):
- Grammar
- Spelling
- Consistency
- Proofreading

## Development

Run tests:
```bash
pytest
```

Run with debug logging:
```bash
LOG_LEVEL=DEBUG uvicorn api.main:app --reload
```
