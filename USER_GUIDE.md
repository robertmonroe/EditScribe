# EditScribe User Guide

## Quick Start Guide

EditScribe is a professional manuscript editing system that follows the same workflow as top-tier publishing houses. This guide will walk you through using the system from start to finish.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Starting the System](#starting-the-system)
3. [Uploading Your Manuscript](#uploading-your-manuscript)
4. [Running the Editorial Workflow](#running-the-editorial-workflow)
5. [Reviewing Results](#reviewing-results)
6. [Understanding Each Stage](#understanding-each-stage)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 14 or higher (for frontend)
- **API Key**: Google Gemini API key (set in `.env` file)

---

## Starting the System

### 1. Start the Backend API

```bash
# Navigate to backend directory
cd c:/Users/3dmax/EditScribe/backend

# Activate virtual environment (if using one)
# On Windows:
venv\Scripts\activate

# Start the FastAPI server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Start the Frontend (Optional)

```bash
# Navigate to frontend directory
cd c:/Users/3dmax/EditScribe/frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

---

## Uploading Your Manuscript

### Via API (Using cURL or Postman)

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/manuscript.docx"
```

**Response:**
```json
{
  "manuscript_id": "abc123-def456-...",
  "filename": "manuscript.docx",
  "word_count": 85000,
  "workflow_status": {...},
  "next_stage": "acquisitions"
}
```

**Important**: Save the `manuscript_id` - you'll need it for all subsequent operations!

---

## Running the Editorial Workflow

The workflow follows a **strict sequential order**. You must complete each stage before moving to the next.

### Stage Order

```
1. Acquisitions Editor
2. Developmental Editor
3. Line Editor
4. Copy Editor
5. Proofreader
6. Cold Reader (Optional)
```

### Running Each Stage

Replace `{manuscript_id}` with your actual manuscript ID from the upload step.

#### 1. Acquisitions Editor (Market Assessment)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/acquisitions"
```

**What it does**: Evaluates market potential, creates editorial letter, identifies comparable titles

**Deliverables**:
- Editorial Letter (3-6 pages)
- Marketing Blurb
- P&L Assessment
- Target Audience Analysis
- Comparable Titles

#### 2. Developmental Editor (Story Structure)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/developmental"
```

**What it does**: Analyzes plot, character arcs, pacing, and story structure

**Deliverables**:
- Plot/character issues
- Pacing problems
- Structural recommendations

#### 3. Line Editor (Prose Polishing)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/line"
```

**What it does**: Polishes prose at sentence level, improves clarity and voice

**Deliverables**:
- Voice/tone issues
- Wordiness problems
- Awkward phrasing fixes

#### 4. Copy Editor (Mechanical Perfection)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/copy"
```

**What it does**: Fixes grammar, enforces house style, checks consistency

**Deliverables**:
- Grammar errors
- Timeline inconsistencies
- Character detail conflicts
- House style violations

#### 5. Proofreader (Final Quality Check)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/proof"
```

**What it does**: Final typo catch and formatting check

**Deliverables**:
- Typos
- Formatting issues
- Final polish

#### 6. Cold Reader (Fresh Eyes - Optional)

```bash
curl -X POST "http://localhost:8000/workflow/{manuscript_id}/cold-read"
```

**What it does**: Provides reader perspective on engagement and clarity

**Deliverables**:
- Reader Report
- Confusion points
- Pacing/engagement issues

---

## Reviewing Results

### Check Workflow Status

```bash
curl "http://localhost:8000/workflow/{manuscript_id}/status"
```

**Response:**
```json
{
  "manuscript_id": "abc123...",
  "workflow": {
    "current_stage": "developmental",
    "acquisitions_status": "completed",
    "developmental_status": "in_progress",
    "line_status": "not_started",
    ...
  },
  "stages_completed": ["acquisitions"]
}
```

### Get Stage Results

```bash
# For Acquisitions (returns full report)
curl "http://localhost:8000/workflow/{manuscript_id}/acquisitions/result"

# For other stages (returns issues list)
curl "http://localhost:8000/workflow/{manuscript_id}/developmental/result"
curl "http://localhost:8000/workflow/{manuscript_id}/line/result"
curl "http://localhost:8000/workflow/{manuscript_id}/copy/result"
curl "http://localhost:8000/workflow/{manuscript_id}/proof/result"
curl "http://localhost:8000/workflow/{manuscript_id}/cold-read/result"
```

### View All Projects

```bash
curl "http://localhost:8000/projects"
```

### Get Complete Editorial Report

```bash
curl "http://localhost:8000/projects/{manuscript_id}/complete-report"
```

---

## Understanding Each Stage

### 📊 Acquisitions Editor
**When to use**: First stage, always required  
**Time**: ~5-10 minutes  
**Focus**: Market viability and commercial potential  
**Output**: Strategic assessment, not line-by-line edits

### 📖 Developmental Editor
**When to use**: After Acquisitions  
**Time**: ~10-20 minutes  
**Focus**: Big-picture story problems  
**Output**: Plot holes, character arc issues, pacing problems

### ✍️ Line Editor
**When to use**: After Developmental (structure is locked)  
**Time**: ~15-30 minutes  
**Focus**: Sentence-level prose quality  
**Output**: Voice, wordiness, syntax improvements

### 📝 Copy Editor
**When to use**: After Line Edit (prose is polished)  
**Time**: ~10-20 minutes  
**Focus**: Grammar, consistency, house style  
**Output**: Mechanical errors, timeline/character conflicts

### 🔍 Proofreader
**When to use**: After Copy Edit (mechanics are fixed)  
**Time**: ~5-10 minutes  
**Focus**: Final typo catch  
**Output**: Spelling, formatting, final polish

### 👀 Cold Reader
**When to use**: After Proofreader (optional)  
**Time**: ~10-15 minutes  
**Focus**: Reader experience and engagement  
**Output**: Reader report, confusion/boredom points

---

## Project File Structure

After processing, your project is saved to:

```
backend/projects/{manuscript_id}/
├── manuscript/
│   ├── original.txt          # Original upload
│   ├── current.txt           # Current version
│   └── versions/             # Stage-by-stage versions
│       ├── acquisitions.txt
│       ├── developmental.txt
│       ├── line.txt
│       ├── copy.txt
│       ├── proof.txt
│       └── cold_read.txt
├── reports/
│   ├── acquisitions_report.json
│   ├── developmental_report.json
│   ├── line_report.json
│   ├── copy_report.json
│   ├── proof_report.json
│   └── cold_read_report.json
├── style_sheet.json          # Story Bible
└── project_data.json         # Workflow status
```

---

## Troubleshooting

### "Cannot run {stage}. Must complete {previous_stage} first."

**Solution**: The workflow is sequential. Complete the previous stage before attempting this one.

```bash
# Check which stage you're on
curl "http://localhost:8000/workflow/{manuscript_id}/status"
```

### "Manuscript not found"

**Solution**: The manuscript ID is incorrect or the project wasn't loaded.

```bash
# List all projects
curl "http://localhost:8000/projects"
```

### API Server Not Running

**Solution**: Start the backend server:

```bash
cd c:/Users/3dmax/EditScribe/backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### LLM API Errors

**Solution**: Check your `.env` file has a valid `GEMINI_API_KEY`:

```bash
# backend/.env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## Example: Complete Workflow

Here's a complete example from upload to final report:

```bash
# 1. Upload manuscript
MANUSCRIPT_ID=$(curl -X POST "http://localhost:8000/upload" \
  -F "file=@manuscript.docx" | jq -r '.manuscript_id')

echo "Manuscript ID: $MANUSCRIPT_ID"

# 2. Run all stages in order
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/acquisitions"
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/developmental"
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/line"
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/copy"
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/proof"
curl -X POST "http://localhost:8000/workflow/$MANUSCRIPT_ID/cold-read"

# 3. Get complete report
curl "http://localhost:8000/projects/$MANUSCRIPT_ID/complete-report" > editorial_report.json

echo "Complete! Check editorial_report.json for results."
```

---

## Tips for Best Results

1. **Start with a complete draft**: The system works best with finished manuscripts
2. **Run stages in order**: Don't skip stages - each builds on the previous
3. **Review each stage**: Check results before moving to the next stage
4. **Use the Style Sheet**: Extract entities first for better consistency checking
5. **Cold Read is optional**: Skip if you're on a tight deadline

---

## Getting Help

- **API Documentation**: Visit `http://localhost:8000/docs` when the server is running
- **Project Files**: Check `backend/projects/{manuscript_id}/` for all outputs
- **Logs**: Check terminal output for detailed processing logs

---

## Next Steps

After completing the workflow:

1. Review the complete editorial report
2. Download the final manuscript version
3. Review the Style Sheet for consistency notes
4. Use the issue lists to guide your revisions

Happy editing! 📚✨
