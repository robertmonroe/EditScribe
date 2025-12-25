# EditScribe

AI-powered professional manuscript editing platform with Series Bible Manager.

## 🎯 What is EditScribe?

EditScribe is a revolutionary manuscript editing tool that delivers professional-quality editing at 95% cost savings:
- **Traditional editing**: $5,500-$15,000 per 50k novel
- **EditScribe**: $99 per manuscript

## ✨ Key Features

### 1. Series Bible Manager (Priority #1)
Automatically extracts and tracks:
- **Characters**: Names, traits, relationships, appearances
- **Locations**: Places, descriptions, significance
- **Timeline**: Dates, events, chronology
- **Objects**: Important items, descriptions

**User reviews and edits the Bible before review agents run** - ensuring accuracy!

### 2. 4-Stage Professional Editing
- **Developmental**: Plot, character arcs, pacing
- **Line Editing**: Prose quality, style, dialogue
- **Copyediting**: Grammar, consistency, spelling
- **Proofreading**: Final polish, typos, formatting

### 3. Smart Multi-LLM Strategy
- **Claude Sonnet 4.5**: Premium agents (judgment, creativity)
- **Gemini 2.5 Flash**: Budget agents (technical, rule-based)

### 4. Selective Fixing
- User selects which issues to fix
- Preview before/after changes
- Accept or reject individual edits

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure API keys:**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and GOOGLE_API_KEY
```

5. **Test Series Bible Manager:**
```bash
python test_bible.py
```

This will extract a Series Bible from a sample manuscript and save it to `test_bible.json`.

## 📁 Project Structure

```
EditScribe/
├── backend/
│   ├── agents/
│   │   ├── base.py                    # Base agent class
│   │   └── series_bible_manager.py    # ✅ COMPLETE
│   ├── api/                           # FastAPI routes (coming soon)
│   ├── core/
│   │   ├── llm_client.py              # ✅ Multi-LLM client
│   │   ├── document_parser.py         # ✅ .docx, .txt, .md parser
│   │   └── models.py                  # ✅ Series Bible data models
│   └── tests/                         # Unit tests
└── frontend/                          # Next.js UI (coming soon)
```

## ✅ What's Built So Far

- [x] Project structure
- [x] LLM client (Claude Sonnet 4.5 + Gemini 2.5 Flash)
- [x] Document parser (.docx, .txt, .md)
- [x] Series Bible Manager
  - [x] Character extraction
  - [x] Location extraction
  - [x] Timeline extraction
  - [x] Object extraction
- [ ] Bible review UI
- [ ] Review agents (Developmental, Line, Copy, Proof)
- [ ] Selective editor
- [ ] Web UI

## 🎯 Next Steps

1. Create FastAPI endpoints for Bible management
2. Build Bible review/edit UI
3. Implement review agents
4. Add selective editing
5. Deploy!

## 💡 Vision

EditScribe will democratize professional editing, making it affordable for every author. By combining AI with user control (Series Bible review), we deliver quality that rivals human editors at a fraction of the cost.

**This is the future of manuscript editing.** 🚀
