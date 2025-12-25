# EditScribe Quick Start

## Option 1: Using the Quick Start Script (Easiest)

### 1. Start the API Server

```bash
cd c:/Users/3dmax/EditScribe/backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run the Quick Start Script

In a **new terminal**:

```bash
cd c:/Users/3dmax/EditScribe
python quick_start.py path/to/your/manuscript.docx
```

That's it! The script will:
- Upload your manuscript
- Run all 6 editorial stages automatically
- Save all results to `./results/` folder

### Options

```bash
# Skip the optional Cold Reader stage
python quick_start.py manuscript.docx --no-cold-read

# Save results to custom directory
python quick_start.py manuscript.docx --output-dir ./my_results
```

---

## Option 2: Manual API Calls

See [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions on using the API directly.

---

## What You'll Get

After running the workflow, you'll have:

### In `./results/` folder:
- `complete_report.json` - Full editorial report
- `acquisitions_report.json` - Market assessment
- `developmental_report.json` - Story structure issues
- `line_report.json` - Prose quality issues
- `copy_report.json` - Grammar/consistency issues
- `proof_report.json` - Typos and formatting
- `cold_read_report.json` - Reader experience feedback

### In `backend/projects/{manuscript_id}/`:
- Original manuscript
- Version after each stage
- Complete project data

---

## Troubleshooting

**"Connection refused"**
- Make sure the API server is running (Step 1)

**"File not found"**
- Check the path to your manuscript file
- Use absolute paths if relative paths don't work

**"API key error"**
- Check `backend/.env` has `GEMINI_API_KEY=your_key_here`

---

## Next Steps

1. Review `complete_report.json` for overview
2. Check individual stage reports for specific issues
3. Use the feedback to revise your manuscript
4. Re-run stages as needed after revisions

For detailed documentation, see [USER_GUIDE.md](USER_GUIDE.md)
