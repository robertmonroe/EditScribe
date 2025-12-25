# Integration Guide for ProjectManager in main.py

## 1. Add Import (line 16, after other imports):
```python
from core.project_manager import ProjectManager
```

## 2. Initialize ProjectManager (line 40, after managing_editor):
```python
project_manager = ProjectManager()
```

## 3. Update upload_manuscript endpoint (after line 76):
```python
# Create project structure
project_manager.create_project(manuscript_id, file.filename.replace(".docx", ""), text)
```

## 4. Update run_acquisitions endpoint (after line 151):
```python
# Save report to disk
project_manager.save_acquisitions_report(manuscript_id, result)
project_manager.save_manuscript_version(manuscript_id, "acquisitions", manuscript_text)
```

## 5. Update run_developmental endpoint (after line 181):
```python
# Save report to disk
project_manager.save_stage_report(manuscript_id, "developmental", [issue.to_dict() for issue in issues])
```

## 6. Update run_line endpoint (after line 211):
```python
# Save report to disk
project_manager.save_stage_report(manuscript_id, "line", [issue.to_dict() for issue in issues])
```

## 7. Update run_copy endpoint (after line 241):
```python
# Save report to disk
project_manager.save_stage_report(manuscript_id, "copy", [issue.to_dict() for issue in issues])
```

## 8. Update run_proof endpoint (after line 271):
```python
# Save report to disk
project_manager.save_stage_report(manuscript_id, "proof", [issue.to_dict() for issue in issues])
```

## 9. Update apply_fixes endpoint (after line 310):
```python
# Save updated manuscript version
project_manager.save_manuscript_version(manuscript_id, f"{stage}_fixes_applied", edited_text)
```

## 10. Add new endpoint to list projects:
```python
@app.get("/projects")
async def list_projects():
    """List all projects"""
    projects = project_manager.list_projects()
    return {"projects": projects}

@app.get("/projects/{manuscript_id}")
async def get_project(manuscript_id: str):
    """Get complete project data"""
    project = project_manager.load_project(manuscript_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/projects/{manuscript_id}/complete-report")
async def get_complete_report(manuscript_id: str):
    """Generate and return complete editorial report"""
    report = project_manager.generate_complete_report(manuscript_id)
    return {"report": report}
```

This will ensure all reports are saved to:
`backend/projects/{manuscript_id}/reports/`

And manuscripts are versioned at:
`backend/projects/{manuscript_id}/manuscript/versions/`
