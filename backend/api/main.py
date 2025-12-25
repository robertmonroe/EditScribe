"""
EditScribe API - Professional Publishing Workflow
Follows industry-standard linear editing (big to small)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
import uuid
import tempfile
import os

import sys
if 'core.llm_client' in sys.modules:
    del sys.modules['core.llm_client']
import core.llm_client
from core.llm_client import LLMClient

# Safety Patch for Reload Failure
if not hasattr(LLMClient, 'generate'):
    print("⚠️ Patching LLMClient.generate due to reload failure")
    def generate_patch(self, prompt, max_tokens=4000, temperature=0.7, context_id=None):
        return self.generate_content(prompt, max_tokens, temperature, context_id=context_id)
    LLMClient.generate = generate_patch

from core.document_parser import DocumentParser
from core.style_sheet import StyleSheet
from core.managing_editor import ManagingEditor, EditingStage
from core.issue import Issue
from core.project_manager import ProjectManager
from core.cancellation import cancellation_manager

# Import professional agents
from agents.acquisitions_editor import AcquisitionsEditor
from agents.developmental_editor import DevelopmentalEditor
from agents.line_editor import LineEditor
from agents.copy_editor import CopyEditor
from agents.proofreader import Proofreader
from agents.cold_reader import ColdReader
from agents.selective_editor_agent import SelectiveEditorAgent

app = FastAPI(title="EditScribe API - Professional Workflow", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
llm_client = LLMClient()
managing_editor = ManagingEditor()
project_manager = ProjectManager()

# Storage (in-memory for now)
manuscripts_storage = {}
style_sheets_storage = {}
stage_results_storage = {}
tasks_storage = {}

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok", 
        "service": "EditScribe API v2.0 - Professional Workflow",
        "llm": {
            "provider": llm_client.current_provider,
            "model": llm_client.current_model
        }
    }


@app.get("/llm/status")
async def get_llm_status():
    """Get current LLM provider status"""
    return {
        "provider": llm_client.current_provider,
        "model": llm_client.current_model,
        "available_providers": ["gemini", "anthropic", "openrouter"]
    }


@app.get("/llm/usage")
async def get_llm_usage():
    """Get LLM token usage statistics"""
    return llm_client.get_usage_stats()


@app.post("/llm/switch")
async def switch_llm_provider(provider: str, model: str = None):
    """Switch LLM provider"""
    try:
        llm_client.switch_provider(provider, model)
        return {
            "success": True,
            "provider": llm_client.current_provider,
            "model": llm_client.current_model
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/debug/llm")
def debug_llm():
    try:
        import inspect
        sig = "unknown"
        if hasattr(llm_client, "generate_content"):
            sig = str(inspect.signature(llm_client.generate_content))
            
        return {
            "attributes": dir(llm_client),
            "has_generate": hasattr(llm_client, "generate"),
            "generate_content_sig": sig
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


@app.post("/upload")
async def upload_manuscript(file: UploadFile = File(...)):
    """Upload manuscript and start workflow"""
    manuscript_id = str(uuid.uuid4())
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{manuscript_id}_{file.filename}")
    
    print(f"DEBUG: Received upload request for {file.filename}")
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"DEBUG: File saved to {temp_path}")
    except Exception as e:
        print(f"DEBUG: Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    try:
        print("DEBUG: Parsing document...")
        text = DocumentParser.parse(temp_path)
        print(f"DEBUG: Document parsed. Length: {len(text)}")
        manuscripts_storage[manuscript_id] = text
        
        style_sheet = StyleSheet(
            manuscript_id=manuscript_id,
            title=file.filename.replace(".docx", ""),
            word_count=len(text.split())
        )
        style_sheets_storage[manuscript_id] = style_sheet
        print("DEBUG: Style sheet created")
        
        # Create project structure on disk
        project_manager.create_project(manuscript_id, file.filename.replace(".docx", ""), text)
        print("DEBUG: Project structure created")
        
        workflow = managing_editor.start_workflow(manuscript_id)
        print("DEBUG: Workflow started")
        
        return {
            "manuscript_id": manuscript_id,
            "filename": file.filename,
            "word_count": style_sheet.word_count,
            "workflow_status": workflow.to_dict(),
            "next_stage": EditingStage.ACQUISITIONS.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing document: {str(e)}")


from core.managing_editor import WorkflowState

def ensure_project_loaded(manuscript_id: str):
    """Ensure project data is loaded from disk into memory"""
    try:
        # Only skip if ALL required data is already in memory
        if (manuscript_id in manuscripts_storage and 
            manuscript_id in style_sheets_storage and 
            manuscript_id in managing_editor.workflows):
            return

        print(f"DEBUG: Loading project {manuscript_id} from disk...")
        project_data = project_manager.load_project(manuscript_id)
        
        if not project_data:
            print(f"DEBUG: Project {manuscript_id} not found on disk")
            return

        # Restore manuscript text
        if project_data.get("current_text"):
            manuscripts_storage[manuscript_id] = project_data["current_text"]
        
        # Restore style sheet
        style_sheet_data = project_manager.load_style_sheet(manuscript_id)
        if style_sheet_data:
            style_sheets_storage[manuscript_id] = StyleSheet(**style_sheet_data)
        else:
            # Create fallback style sheet from metadata if none exists
            metadata = project_data.get("metadata", {})
            print(f"DEBUG: No style sheet found, creating fallback from metadata")
            style_sheets_storage[manuscript_id] = StyleSheet(
                manuscript_id=manuscript_id,
                title=metadata.get("title", "Untitled"),
                word_count=len(project_data.get("current_text", "").split())
            )
            # Save it for next time
            project_manager.save_style_sheet(manuscript_id, style_sheets_storage[manuscript_id].to_dict())
            
        # Restore workflow status
        workflow_data = project_data.get("workflow")
        if workflow_data:
            # Reconstruct WorkflowState object
            current_stage = None
            if workflow_data.get("current_stage"):
                try:
                    current_stage = EditingStage(workflow_data["current_stage"])
                except ValueError:
                    print(f"WARNING: Invalid current_stage {workflow_data['current_stage']}")
            
            # Map status strings to StageStatus enum
            from core.managing_editor import StageStatus
            
            def get_status(key):
                val = workflow_data.get(key, "not_started")
                try:
                    return StageStatus(val)
                except ValueError:
                    return StageStatus.NOT_STARTED

            workflow = WorkflowState(
                manuscript_id=workflow_data["manuscript_id"],
                current_stage=current_stage,
                
                # Restore individual stage statuses
                acquisitions_status=get_status("acquisitions_status"),
                developmental_status=get_status("developmental_status"),
                line_status=get_status("line_status"),
                copy_status=get_status("copy_status"),
                proof_status=get_status("proof_status"),
                cold_read_status=get_status("cold_read_status"),
                
                started_at=workflow_data.get("started_at"),
                completed_at=workflow_data.get("completed_at"),
                total_issues_found=workflow_data.get("total_issues_found", 0),
                total_fixes_applied=workflow_data.get("total_fixes_applied", 0)
            )
            managing_editor.workflows[manuscript_id] = workflow
            print(f"DEBUG: Workflow state restored for {manuscript_id}")
            print(f"DEBUG: Acquisitions status: {workflow.acquisitions_status}")
            
    except Exception as e:
        print(f"ERROR in ensure_project_loaded: {e}")
        import traceback
        traceback.print_exc()


async def _run_entity_extraction_task(task_id: str, manuscript_id: str):
    """Background task for entity extraction (World Building)"""
    try:
        from agents.style_sheet_extractor import StyleSheetExtractor
        
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        # Define progress callback
        async def update_progress(message: str, percent: int):
            tasks_storage[task_id]["progress"] = percent
            tasks_storage[task_id]["message"] = message
            
        # Extract entities using LLM
        extractor = StyleSheetExtractor(llm_client)
        print(f"DEBUG: Starting entity extraction for {manuscript_id}")
        style_sheet = await extractor.extract_world_building(manuscript_text, style_sheet, on_progress=update_progress)
        print("DEBUG: Entity extraction finished")
        
        # Update storage
        style_sheets_storage[manuscript_id] = style_sheet
        
        # Save to disk
        project_manager.save_style_sheet(manuscript_id, style_sheet.to_dict())
        
        tasks_storage[task_id] = {
            "status": "completed",
            "result": {
                "manuscript_id": manuscript_id,
                "bible": style_sheet.to_dict(),
                "stats": {
                    "characters": len(style_sheet.characters),
                    "locations": len(style_sheet.locations),
                    "timeline_events": len(style_sheet.timeline),
                    "objects": len(style_sheet.objects)
                }
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        tasks_storage[task_id] = {
            "status": "failed",
            "error": str(e)
        }

async def _run_synopsis_task(task_id: str, manuscript_id: str):
    """Background task for synopsis generation"""
    try:
        from agents.style_sheet_extractor import StyleSheetExtractor
        
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        extractor = StyleSheetExtractor(llm_client)
        print(f"DEBUG: Starting synopsis generation for {manuscript_id}")
        style_sheet = await extractor.generate_synopsis(manuscript_text, style_sheet)
        print("DEBUG: Synopsis generation finished")
        
        # Update storage
        style_sheets_storage[manuscript_id] = style_sheet
        
        # Save to disk
        project_manager.save_style_sheet(manuscript_id, style_sheet.to_dict())
        
        tasks_storage[task_id] = {
            "status": "completed",
            "result": {
                "manuscript_id": manuscript_id,
                "bible": style_sheet.to_dict(),
                "synopsis": style_sheet.synopsis
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        tasks_storage[task_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.post("/bible/extract/entities/{manuscript_id}")
async def extract_entities(manuscript_id: str, background_tasks: BackgroundTasks):
    """Start asynchronous Entity Extraction (World Building)"""
    ensure_project_loaded(manuscript_id)
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    if manuscript_id not in style_sheets_storage:
        raise HTTPException(status_code=404, detail="Style Sheet not found")
    
    task_id = str(uuid.uuid4())
    tasks_storage[task_id] = {"status": "running", "progress": 0, "message": "Initializing..."}
    
    background_tasks.add_task(_run_entity_extraction_task, task_id, manuscript_id)
    
    return {"task_id": task_id, "status": "running"}

@app.post("/bible/extract/synopsis/{manuscript_id}")
async def extract_synopsis(manuscript_id: str, background_tasks: BackgroundTasks):
    """Start asynchronous Synopsis Generation"""
    ensure_project_loaded(manuscript_id)
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    if manuscript_id not in style_sheets_storage:
        raise HTTPException(status_code=404, detail="Style Sheet not found")
    
    task_id = str(uuid.uuid4())
    tasks_storage[task_id] = {"status": "running", "progress": 0, "message": "Generating Synopsis..."}
    
    background_tasks.add_task(_run_synopsis_task, task_id, manuscript_id)
    
    return {"task_id": task_id, "status": "running"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a background task"""
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_storage[task_id]


@app.post("/workflow/{manuscript_id}/acquisitions")
async def run_acquisitions(manuscript_id: str):
    """Run Acquisitions Editor (Stage 1)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.ACQUISITIONS)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = AcquisitionsEditor(llm_client)
        agent.set_context(manuscript_id)
        result = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["acquisitions"] = {
            "report": result,
            "issues": []
        }
        
        # Save report to disk
        project_manager.save_acquisitions_report(manuscript_id, result)
        project_manager.save_manuscript_version(manuscript_id, "acquisitions", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id, 
            EditingStage.ACQUISITIONS,
            issues_found=0,
            fixes_applied=0
        )
        
        # Save workflow status
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "acquisitions",
            "status": "complete",
            "report": result,
            "next_stage": workflow.current_stage.value if workflow.current_stage else None
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Acquisitions failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/developmental")
async def run_developmental(manuscript_id: str):
    """Run Developmental Editor (Stage 2)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.DEVELOPMENTAL)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = DevelopmentalEditor(llm_client)
        agent.set_context(manuscript_id)
        issues = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["developmental"] = {
            "issues": [issue.to_dict() for issue in issues],
            "fixes_applied": 0
        }
        
        # Save report to disk
        project_manager.save_stage_report(manuscript_id, "developmental", [issue.to_dict() for issue in issues])
        project_manager.save_manuscript_version(manuscript_id, "developmental", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id,
            EditingStage.DEVELOPMENTAL,
            issues_found=len(issues),
            fixes_applied=0
        )
        
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "developmental",
            "total_issues": len(issues),
            "issues": [issue.to_dict() for issue in issues]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Developmental failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/line")
async def run_line(manuscript_id: str):
    """Run Line Editor (Stage 3)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.LINE)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = LineEditor(llm_client)
        agent.set_context(manuscript_id)
        issues = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["line"] = {
            "issues": [issue.to_dict() for issue in issues],
            "fixes_applied": 0
        }
        
        # Save report to disk
        project_manager.save_stage_report(manuscript_id, "line", [issue.to_dict() for issue in issues])
        project_manager.save_manuscript_version(manuscript_id, "line", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id,
            EditingStage.LINE,
            issues_found=len(issues),
            fixes_applied=0
        )
        
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "line",
            "total_issues": len(issues),
            "issues": [issue.to_dict() for issue in issues]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Line editing failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/copy")
async def run_copy(manuscript_id: str):
    """Run Copy Editor (Stage 4)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.COPY)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = CopyEditor(llm_client)
        agent.set_context(manuscript_id)
        issues = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["copy"] = {
            "issues": [issue.to_dict() for issue in issues],
            "fixes_applied": 0
        }
        
        # Save report to disk
        project_manager.save_stage_report(manuscript_id, "copy", [issue.to_dict() for issue in issues])
        project_manager.save_manuscript_version(manuscript_id, "copy", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id,
            EditingStage.COPY,
            issues_found=len(issues),
            fixes_applied=0
        )
        
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "copy",
            "total_issues": len(issues),
            "issues": [issue.to_dict() for issue in issues]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Copyediting failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/proof")
async def run_proof(manuscript_id: str):
    """Run Proofreader (Stage 5)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.PROOF)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = Proofreader(llm_client)
        agent.set_context(manuscript_id)
        issues = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["proof"] = {
            "issues": [issue.to_dict() for issue in issues],
            "fixes_applied": 0
        }
        
        # Save report to disk
        project_manager.save_stage_report(manuscript_id, "proof", [issue.to_dict() for issue in issues])
        project_manager.save_manuscript_version(manuscript_id, "proof", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id,
            EditingStage.PROOF,
            issues_found=len(issues),
            fixes_applied=0
        )
        
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "proof",
            "total_issues": len(issues),
            "issues": [issue.to_dict() for issue in issues]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Proofreading failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/cold-read")
async def run_cold_read(manuscript_id: str):
    """Run Cold Reader (Stage 6 - Optional)"""
    ensure_project_loaded(manuscript_id)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.COLD_READ)
    if not can_run:
        raise HTTPException(status_code=400, detail=reason)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        cancellation_manager.reset(manuscript_id)
        manuscript_text = manuscripts_storage[manuscript_id]
        style_sheet = style_sheets_storage[manuscript_id]
        
        agent = ColdReader(llm_client)
        agent.set_context(manuscript_id)
        result = agent.execute(manuscript_text, style_sheet)
        
        if manuscript_id not in stage_results_storage:
            stage_results_storage[manuscript_id] = {}
        
        stage_results_storage[manuscript_id]["cold_read"] = result
        
        # Save report to disk
        project_manager.save_stage_report(manuscript_id, "cold_read", result)
        project_manager.save_manuscript_version(manuscript_id, "cold_read", manuscript_text)
        
        workflow = managing_editor.mark_stage_complete(
            manuscript_id,
            EditingStage.COLD_READ,
            issues_found=result.get("total_issues", 0),
            fixes_applied=0
        )
        
        project_manager.save_workflow_status(manuscript_id, workflow.to_dict())
        
        return {
            "stage": "cold_read",
            "status": "complete",
            "reader_report": result.get("reader_report", ""),
            "total_issues": result.get("total_issues", 0),
            "issues": result.get("issues", []),
            "workflow_complete": workflow.completed_at is not None
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Cold read failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/cancel")
async def cancel_stage(manuscript_id: str):
    """Cancel any running stage for a manuscript"""
    cancellation_manager.cancel(manuscript_id)
    return {"success": True, "message": "Cancellation requested"}


from pydantic import BaseModel
from typing import List

class ApplyFixesRequest(BaseModel):
    issue_indices: List[int]

# @app.post("/workflow/{manuscript_id}/{stage}/apply-fixes")
# async def apply_fixes(manuscript_id: str, stage: str, request: ApplyFixesRequest):
#     """Apply fixes for a specific stage"""
#     if manuscript_id not in manuscripts_storage:
#         raise HTTPException(status_code=404, detail="Manuscript not found")
    
#     if manuscript_id not in stage_results_storage or stage not in stage_results_storage[manuscript_id]:
#         raise HTTPException(status_code=404, detail=f"No issues found for {stage} stage")
    
#     try:
#         manuscript_text = manuscripts_storage[manuscript_id]
#         style_sheet = style_sheets_storage[manuscript_id]
#         issues_data = stage_results_storage[manuscript_id][stage]["issues"]
        
#         # Filter issues based on indices
#         selected_issues_data = [issues_data[i] for i in request.issue_indices if 0 <= i < len(issues_data)]
        
#         # Convert dict issues back to Issue objects
#         issues = [Issue(**issue_dict) for issue_dict in selected_issues_data]
        
#         # Use SelectiveEditorAgent to apply fixes
#         # editor = SelectiveEditorAgent(llm_client)
#         # result = editor.execute(manuscript_text, issues)
        
#         # # Update manuscript
#         # manuscripts_storage[manuscript_id] = result["edited_text"]
        
#         # # Save version with fixes applied
#         # project_manager.save_manuscript_version(manuscript_id, f"{stage}_fixes_applied", result["edited_text"])
        
#         # # Update stage results
#         # stage_results_storage[manuscript_id][stage]["fixes_applied"] = result["fixes_applied"]
        
#         # return {
#         #     "edited_text": result["edited_text"],
#         #     "fixes_applied": result["fixes_applied"],
#         #     "stage": stage,
#         #     "change_log": result.get("change_log", [])
#         # }
#         pass
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Fix application failed: {str(e)}")


@app.get("/workflow/{manuscript_id}/status")
async def get_workflow_status(manuscript_id: str):
    """Get current workflow status"""
    ensure_project_loaded(manuscript_id)
    workflow = managing_editor.get_workflow_status(manuscript_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "manuscript_id": manuscript_id,
        "workflow": workflow.to_dict(),
        "stages_completed": [
            stage for stage in ["acquisitions", "developmental", "line", "copy", "proof"]
            if manuscript_id in stage_results_storage and stage in stage_results_storage[manuscript_id]
        ]
    }


@app.get("/manuscript/{manuscript_id}")
async def get_manuscript(manuscript_id: str):
    """Get current manuscript text"""
    ensure_project_loaded(manuscript_id)
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    return {
        "manuscript_id": manuscript_id,
        "text": manuscripts_storage[manuscript_id],
        "word_count": len(manuscripts_storage[manuscript_id].split())
    }


@app.get("/manuscript/{manuscript_id}/version/{version_name}")
async def get_manuscript_version(manuscript_id: str, version_name: str):
    """Get a specific version of the manuscript"""
    ensure_project_loaded(manuscript_id)
    
    project_dir = project_manager.base_dir / manuscript_id
    
    # Handle special cases
    if version_name == "original":
        version_file = project_dir / "manuscript" / "original.txt"
    elif version_name == "current":
        version_file = project_dir / "manuscript" / "current.txt"
    else:
        version_file = project_dir / "manuscript" / "versions" / f"{version_name}.txt"
    
    if not version_file.exists():
        raise HTTPException(status_code=404, detail=f"Version '{version_name}' not found")
    
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        return {
            "manuscript_id": manuscript_id,
            "version": version_name,
            "text": text,
            "word_count": len(text.split())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read version: {str(e)}")


@app.get("/workflow/{manuscript_id}/diff")
async def get_version_diff(manuscript_id: str, v1: str = "original", v2: str = "current"):
    """Compare two versions of a manuscript"""
    try:
        ensure_project_loaded(manuscript_id)
        changes = project_manager.compare_versions(manuscript_id, v1, v2)
        return {
            "manuscript_id": manuscript_id,
            "v1": v1,
            "v2": v2,
            "changes": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diff generation failed: {str(e)}")


@app.get("/workflow/{manuscript_id}/download")
async def download_manuscript(manuscript_id: str):
    """Download the current version of the manuscript"""
    try:
        ensure_project_loaded(manuscript_id)
        
        # Check if project exists
        project_dir = project_manager.base_dir / manuscript_id
        if not project_dir.exists():
             raise HTTPException(status_code=404, detail="Project not found")
        
        # Get current text - try multiple locations
        current_file = project_dir / "manuscript" / "current.txt"
        
        if not current_file.exists():
            current_file = project_dir / "versions" / "current.txt"
        
        if not current_file.exists():
            current_file = project_dir / "current.txt"
            
        if not current_file.exists():
            raise HTTPException(status_code=404, detail="Manuscript file not found")
            
        with open(current_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Create filename
        filename = f"manuscript_{manuscript_id[:8]}.txt"
        
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prepare download: {str(e)}")


@app.get("/workflow/{manuscript_id}/versions")
async def list_versions(manuscript_id: str):
    """List manuscript versions"""
    ensure_project_loaded(manuscript_id)
    versions = project_manager.list_versions(manuscript_id)
    return {"versions": versions}


@app.post("/workflow/{manuscript_id}/restore")
async def restore_version(manuscript_id: str, version: str):
    """Restore a specific version"""
    ensure_project_loaded(manuscript_id)
    success = project_manager.restore_version(manuscript_id, version)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Reload into memory
    try:
        project_dir = project_manager.base_dir / manuscript_id
        current_file = project_dir / "manuscript" / "current.txt"
        with open(current_file, "r", encoding="utf-8") as f:
            manuscripts_storage[manuscript_id] = f.read()
    except Exception as e:
        print(f"Error reloading manuscript: {e}")
        
    return {"success": True, "message": f"Restored version {version}"}


@app.get("/style-sheet/{manuscript_id}")
async def get_style_sheet(manuscript_id: str):
    """Get Style Sheet"""
    ensure_project_loaded(manuscript_id)
    if manuscript_id not in style_sheets_storage:
        raise HTTPException(status_code=404, detail="Style Sheet not found")
    
    return style_sheets_storage[manuscript_id].to_dict()


@app.put("/style-sheet/{manuscript_id}")
async def update_style_sheet(manuscript_id: str, updates: dict):
    """Update Style Sheet"""
    if manuscript_id not in style_sheets_storage:
        raise HTTPException(status_code=404, detail="Style Sheet not found")
    
    style_sheet = style_sheets_storage[manuscript_id]
    
    # Update fields
    for key, value in updates.items():
        if hasattr(style_sheet, key):
            setattr(style_sheet, key, value)
    
    # Save to disk
    project_manager.save_style_sheet(manuscript_id, style_sheet.to_dict())
    
    return style_sheet.to_dict()


@app.get("/project/{manuscript_id}/status")
async def get_project_status(manuscript_id: str):
    """Get the comprehensive status of the project workflow"""
    ensure_project_loaded(manuscript_id)
    
    workflow = managing_editor.get_workflow_status(manuscript_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {
        "manuscript_id": manuscript_id,
        "current_stage": workflow.current_stage,
        "stages": {
            "acquisitions": workflow.acquisitions_status,
            "developmental": workflow.developmental_status,
            "line": workflow.line_status,
            "copy": workflow.copy_status,
            "proof": workflow.proof_status,
            "cold_read": workflow.cold_read_status if hasattr(workflow, 'cold_read_status') else "not_started"
        }
    }
@app.get("/workflow/{manuscript_id}/{stage}/result")
async def get_stage_result(manuscript_id: str, stage: str):
    """Get result of a completed stage"""
    print(f"DEBUG: get_stage_result called for {manuscript_id}, stage={stage}")
    with open("debug_output_5.txt", "a") as f:
        f.write(f"get_stage_result called: id={manuscript_id}, stage='{stage}'\n")
    ensure_project_loaded(manuscript_id)
    try:
        result = {"stage": stage, "status": "complete"}
        
        if stage == "acquisitions":
            report = project_manager.load_acquisitions_report(manuscript_id)
            if report:
                result["report"] = report
            else:
                raise HTTPException(status_code=404, detail="Report not found")
        elif stage == "cold_read":
            # Cold read has both reader_report and issues
            stage_data = project_manager.load_stage_report(manuscript_id, stage)
            if stage_data:
                result["reader_report"] = stage_data.get("reader_report", "")
                result["issues"] = stage_data.get("issues", [])
                result["total_issues"] = stage_data.get("total_issues", 0)
            else:
                raise HTTPException(status_code=404, detail="Cold read report not found")
        else:
            # Issue-based stages
            stage_data = project_manager.load_stage_report(manuscript_id, stage)
            if stage_data and "issues" in stage_data:
                result["issues"] = stage_data["issues"]
                result["total_issues"] = len(result["issues"])
            else:
                raise HTTPException(status_code=404, detail="Issues not found")
                
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load result: {str(e)}")


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
    
    # Flatten the response for frontend compatibility
    # Frontend expects title/word_count at top level, not nested in metadata
    metadata = project.get("metadata", {})
    return {
        "manuscript_id": manuscript_id,
        "title": metadata.get("title", "Untitled"),
        "word_count": metadata.get("word_count", 0),
        "workflow": project.get("workflow", {}),
        "current_text": project.get("current_text", ""),
        # Include remaining metadata fields
        "created_at": metadata.get("created_at"),
        "last_modified": metadata.get("last_modified"),
        "original_filename": metadata.get("original_filename"),
    }


@app.delete("/projects/{manuscript_id}")
async def delete_project(manuscript_id: str):
    """Delete a project and all its files"""
    # Delete from disk
    success = project_manager.delete_project(manuscript_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Clear from in-memory storage
    if manuscript_id in manuscripts_storage:
        del manuscripts_storage[manuscript_id]
    if manuscript_id in style_sheets_storage:
        del style_sheets_storage[manuscript_id]
    if manuscript_id in stage_results_storage:
        del stage_results_storage[manuscript_id]
    if manuscript_id in managing_editor.workflows:
        del managing_editor.workflows[manuscript_id]
    
    return {"status": "deleted", "manuscript_id": manuscript_id}


@app.post("/projects/{manuscript_id}/duplicate")
async def duplicate_project(manuscript_id: str):
    """Duplicate/Backup a project"""
    metadata = project_manager.duplicate_project(manuscript_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Project not found or failed to duplicate")
    return metadata


class RenameProjectRequest(BaseModel):
    title: str

@app.put("/projects/{manuscript_id}/rename")
async def rename_project(manuscript_id: str, request: RenameProjectRequest):
    """Rename a project"""
    success = project_manager.rename_project(manuscript_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or failed to rename")
    return {"success": True, "title": request.title}


@app.get("/projects/{manuscript_id}/complete-report")
async def get_complete_report(manuscript_id: str):
    """Generate complete editorial report"""
    try:
        report = project_manager.generate_complete_report(manuscript_id)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@app.post("/workflow/{manuscript_id}/apply-fix")
async def apply_fix(manuscript_id: str, issue_data: dict):
    """Apply a single fix to the manuscript using SelectiveEditorAgent"""
    ensure_project_loaded(manuscript_id)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    try:
        manuscript_text = manuscripts_storage[manuscript_id]
        
        # Create Issue object from the data
        issue = Issue(
            id=issue_data.get("id", 0),
            stage=issue_data.get("stage", "unknown"),
            severity=issue_data.get("severity", "minor"),
            category=issue_data.get("category", "general"),
            location=issue_data.get("location", ""),
            original_text=issue_data.get("original_text", issue_data.get("quote", "")),
            description=issue_data.get("description", issue_data.get("issue", "")),
            suggestion=issue_data.get("suggestion", ""),
            bible_conflict=issue_data.get("bible_conflict", False)
        )
        
        # Apply the fix using SelectiveEditorAgent
        agent = SelectiveEditorAgent(llm_client)
        result = agent.execute(manuscript_text, [issue])
        
        if result["fixes_applied"] > 0:
            # Update in-memory manuscript
            manuscripts_storage[manuscript_id] = result["edited_text"]
            
            # Save to disk
            project_manager.save_manuscript_version(manuscript_id, "edited", result["edited_text"])
            
            # Update issue status
            if manuscript_id in stage_results_storage and issue.stage in stage_results_storage[manuscript_id]:
                issues_list = stage_results_storage[manuscript_id][issue.stage].get("issues", [])
                for i, existing_issue in enumerate(issues_list):
                    if existing_issue.get("id") == issue.id:
                        issues_list[i]["status"] = "applied"
                        project_manager.save_stage_report(manuscript_id, issue.stage, issues_list)
                        break
            
            return {
                "success": True,
                "fixes_applied": result["fixes_applied"],
                "change_log": result["change_log"],
                "message": "Fix applied successfully"
            }
        else:
            return {
                "success": False,
                "fixes_applied": 0,
                "message": "Could not apply fix - text may not match"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to apply fix: {str(e)}")



@app.post("/workflow/{manuscript_id}/apply-batch-fixes")
async def apply_batch_fixes(manuscript_id: str, batch_data: dict):
    """Apply multiple fixes to the manuscript at once"""
    ensure_project_loaded(manuscript_id)
    
    stage = batch_data.get("stage")
    issues_data = batch_data.get("issues", [])
    
    if not stage or not issues_data:
        raise HTTPException(status_code=400, detail="Missing stage or issues data")
        
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
        
    try:
        manuscript_text = manuscripts_storage[manuscript_id]
        issue_objects = []
        
        # Convert dicts to Issue objects
        for data in issues_data:
            issue_objects.append(Issue(
                id=data.get("id", 0),
                stage=stage,
                severity=data.get("severity", "minor"),
                category=data.get("category", "general"),
                location=data.get("location", ""),
                original_text=data.get("original_text", data.get("quote", "")),
                description=data.get("description", data.get("issue", "")),
                suggestion=data.get("suggestion", ""),
                bible_conflict=data.get("bible_conflict", False)
            ))
            
        # Apply fixes
        agent = SelectiveEditorAgent(llm_client)
        result = agent.execute(manuscript_text, issue_objects)
        
        if result["fixes_applied"] > 0:
            # Update storage
            manuscripts_storage[manuscript_id] = result["edited_text"]
            project_manager.save_manuscript_version(manuscript_id, "edited", result["edited_text"])
            
            # Update statuses
            if manuscript_id in stage_results_storage and stage in stage_results_storage[manuscript_id]:
                server_issues = stage_results_storage[manuscript_id][stage].get("issues", [])
                applied_ids = {i.id for i in issue_objects}
                
                for i, existing in enumerate(server_issues):
                    if existing.get("id") in applied_ids:
                        server_issues[i]["status"] = "applied"
                
                project_manager.save_stage_report(manuscript_id, stage, server_issues)
                
            return {
                "success": True,
                "fixes_applied": result["fixes_applied"],
                "message": f"Successfully applied {result['fixes_applied']} fixes"
            }
        else:
            return {
                "success": False, 
                "fixes_applied": 0,
                "message": "No fixes were applied (possible text mismatch)"
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Batch apply failed: {str(e)}")


@app.post("/workflow/{manuscript_id}/ignore-issue")
async def ignore_issue(manuscript_id: str, issue_data: dict):
    """Mark an issue as ignored"""
    ensure_project_loaded(manuscript_id)
    
    stage = issue_data.get("stage")
    issue_id = issue_data.get("id")
    
    if not stage or issue_id is None:
        print(f"DEBUG: Missing stage or id. stage={stage}, id={issue_id}")
        raise HTTPException(status_code=400, detail="Missing stage or issue ID")
        
    try:
        # Load directly from disk to ensure fresh data
        stage_report = project_manager.load_stage_report(manuscript_id, stage)
        
        # Handle Cold Read structure
        if stage == "cold_read":
             issues_list = stage_report.get("issues", [])
        elif stage_report and "issues" in stage_report:
             issues_list = stage_report["issues"]
        else:
             print(f"DEBUG: No issues found for stage {stage}")
             raise HTTPException(status_code=404, detail="No results found for this stage")
             
        found = False
        
        # Find and update
        for i, issue in enumerate(issues_list):
            # Handle int/str mismatch in IDs
            if str(issue.get("id")) == str(issue_id):
                issues_list[i]["status"] = "ignored"
                found = True
                break
                
        if not found:
            print(f"DEBUG: Issue {issue_id} not found in {len(issues_list)} issues")
            raise HTTPException(status_code=404, detail="Issue not found")
            
        # Save updated report
        project_manager.save_stage_report(manuscript_id, stage, issues_list if stage != "cold_read" else stage_report)
        
        # Update cache if present
        if manuscript_id in stage_results_storage and stage in stage_results_storage[manuscript_id]:
             # Re-load from disk to cache to be safe, or just update cache
             if stage == "cold_read":
                 stage_results_storage[manuscript_id][stage] = stage_report
             else:
                 stage_results_storage[manuscript_id][stage]["issues"] = issues_list
        
        return {"success": True, "message": "Issue ignored"}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to ignore issue: {str(e)}")


@app.post("/workflow/{manuscript_id}/unignore-issue")
async def unignore_issue(manuscript_id: str, issue_data: dict):
    """Mark an issue as un-ignored (open)"""
    ensure_project_loaded(manuscript_id)
    
    stage = issue_data.get("stage")
    issue_id = issue_data.get("id")
    
    if not stage or issue_id is None:
        raise HTTPException(status_code=400, detail="Missing stage or issue ID")
        
    try:
        # Load directly from disk to ensure fresh data
        stage_report = project_manager.load_stage_report(manuscript_id, stage)
        
        # Handle Cold Read structure
        if stage == "cold_read":
             issues_list = stage_report.get("issues", [])
        elif stage_report and "issues" in stage_report:
             issues_list = stage_report["issues"]
        else:
             raise HTTPException(status_code=404, detail="No results found for this stage")
             
        found = False
        
        # Find and update
        for i, issue in enumerate(issues_list):
            if str(issue.get("id")) == str(issue_id):
                # Restore to 'open' - or 'applied' if it was applied? 
                # Assuming 'unignore' means 'I want to see it again to decide', so 'open'.
                issues_list[i]["status"] = "open"
                found = True
                break
                
        if not found:
            raise HTTPException(status_code=404, detail="Issue not found")
            
        # Save updated report
        project_manager.save_stage_report(manuscript_id, stage, issues_list if stage != "cold_read" else stage_report)
        
        # Update cache if present
        if manuscript_id in stage_results_storage and stage in stage_results_storage[manuscript_id]:
             if stage == "cold_read":
                 stage_results_storage[manuscript_id][stage] = stage_report
             else:
                 stage_results_storage[manuscript_id][stage]["issues"] = issues_list
        
        return {"success": True, "message": "Issue un-ignored"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to un-ignore issue: {str(e)}")


@app.get("/workflow/{manuscript_id}/manuscript")
async def get_manuscript(manuscript_id: str):
    """Get the current manuscript text"""
    ensure_project_loaded(manuscript_id)
    
    if manuscript_id not in manuscripts_storage:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    return {
        "manuscript_id": manuscript_id,
        "text": manuscripts_storage[manuscript_id],
        "word_count": len(manuscripts_storage[manuscript_id].split())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
