"""
Managing Editor - Workflow Orchestrator
Traffic controller that enforces sequential editing order
"""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class EditingStage(str, Enum):
    """Professional editing stages in sequential order"""
    ACQUISITIONS = "acquisitions"
    DEVELOPMENTAL = "developmental"
    LINE = "line"
    COPY = "copy"
    PROOF = "proof"
    COLD_READ = "cold_read"


class StageStatus(str, Enum):
    """Status of each editing stage"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class WorkflowState(BaseModel):
    """Current state of the editing workflow"""
    manuscript_id: str
    current_stage: Optional[EditingStage] = None
    
    # Stage statuses
    acquisitions_status: StageStatus = StageStatus.NOT_STARTED
    developmental_status: StageStatus = StageStatus.NOT_STARTED
    line_status: StageStatus = StageStatus.NOT_STARTED
    copy_status: StageStatus = StageStatus.NOT_STARTED
    proof_status: StageStatus = StageStatus.NOT_STARTED
    cold_read_status: StageStatus = StageStatus.NOT_STARTED
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    total_issues_found: int = 0
    total_fixes_applied: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary with proper datetime serialization"""
        return self.model_dump(mode='json')


class ManagingEditor:
    """
    Managing Editor - Traffic Controller for Editorial Workflow
    
    Responsibilities:
    - Enforce sequential order (cannot skip stages)
    - Declare stages "Complete"
    - Trigger next agent
    - Track workflow progress
    - Generate reports
    
    Does NOT edit text - only manages the workflow.
    """
    
    # Define the strict sequential order
    STAGE_ORDER = [
        EditingStage.ACQUISITIONS,
        EditingStage.DEVELOPMENTAL,
        EditingStage.LINE,
        EditingStage.COPY,
        EditingStage.PROOF,
        EditingStage.COLD_READ
    ]
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowState] = {}
    
    def start_workflow(self, manuscript_id: str) -> WorkflowState:
        """
        Start a new editing workflow.
        
        Args:
            manuscript_id: Manuscript ID
            
        Returns:
            Initial workflow state
        """
        workflow = WorkflowState(
            manuscript_id=manuscript_id,
            current_stage=EditingStage.ACQUISITIONS,
            started_at=datetime.now()
        )
        
        self.workflows[manuscript_id] = workflow
        return workflow
    
    def can_run_stage(self, manuscript_id: str, stage: EditingStage) -> tuple[bool, str]:
        """
        Check if a stage can be run (enforces sequential order).
        
        Args:
            manuscript_id: Manuscript ID
            stage: Stage to check
            
        Returns:
            (can_run, reason)
        """
        if manuscript_id not in self.workflows:
            return False, "Workflow not started. Call start_workflow() first."
        
        workflow = self.workflows[manuscript_id]
        
        # Get the index of the requested stage
        try:
            stage_index = self.STAGE_ORDER.index(stage)
        except ValueError:
            return False, f"Invalid stage: {stage}"
        
        # Check if all previous stages are completed
        for i in range(stage_index):
            prev_stage = self.STAGE_ORDER[i]
            prev_status = self._get_stage_status(workflow, prev_stage)
            
            if prev_status != StageStatus.COMPLETED and prev_status != StageStatus.SKIPPED:
                return False, f"Cannot run {stage.value}. Must complete {prev_stage.value} first."
        
        return True, "OK"
    
    def mark_stage_complete(self, manuscript_id: str, stage: EditingStage, 
                           issues_found: int = 0, fixes_applied: int = 0) -> WorkflowState:
        """
        Mark a stage as complete and advance to next stage.
        
        Args:
            manuscript_id: Manuscript ID
            stage: Stage to mark complete
            issues_found: Number of issues found
            fixes_applied: Number of fixes applied
            
        Returns:
            Updated workflow state
        """
        if manuscript_id not in self.workflows:
            raise ValueError("Workflow not started")
        
        workflow = self.workflows[manuscript_id]
        
        # Update stage status
        self._set_stage_status(workflow, stage, StageStatus.COMPLETED)
        
        # Update totals
        workflow.total_issues_found += issues_found
        workflow.total_fixes_applied += fixes_applied
        
        # Advance to next stage
        next_stage = self._get_next_stage(stage)
        if next_stage:
            workflow.current_stage = next_stage
        else:
            # Workflow complete
            workflow.current_stage = None
            workflow.completed_at = datetime.now()
        
        return workflow
    
    def skip_stage(self, manuscript_id: str, stage: EditingStage) -> WorkflowState:
        """
        Skip a stage (for optional stages like Cold Read).
        
        Args:
            manuscript_id: Manuscript ID
            stage: Stage to skip
            
        Returns:
            Updated workflow state
        """
        if manuscript_id not in self.workflows:
            raise ValueError("Workflow not started")
        
        workflow = self.workflows[manuscript_id]
        self._set_stage_status(workflow, stage, StageStatus.SKIPPED)
        
        # Advance to next stage
        next_stage = self._get_next_stage(stage)
        if next_stage:
            workflow.current_stage = next_stage
        
        return workflow
    
    def get_workflow_status(self, manuscript_id: str) -> Optional[WorkflowState]:
        """Get current workflow status"""
        return self.workflows.get(manuscript_id)
    
    def get_next_available_stage(self, manuscript_id: str) -> Optional[EditingStage]:
        """Get the next stage that can be run"""
        if manuscript_id not in self.workflows:
            return None
        
        workflow = self.workflows[manuscript_id]
        return workflow.current_stage
    
    def is_workflow_complete(self, manuscript_id: str) -> bool:
        """Check if workflow is complete"""
        if manuscript_id not in self.workflows:
            return False
        
        workflow = self.workflows[manuscript_id]
        return workflow.completed_at is not None
    
    def _get_stage_status(self, workflow: WorkflowState, stage: EditingStage) -> StageStatus:
        """Get status of a specific stage"""
        status_map = {
            EditingStage.ACQUISITIONS: workflow.acquisitions_status,
            EditingStage.DEVELOPMENTAL: workflow.developmental_status,
            EditingStage.LINE: workflow.line_status,
            EditingStage.COPY: workflow.copy_status,
            EditingStage.PROOF: workflow.proof_status,
            EditingStage.COLD_READ: workflow.cold_read_status
        }
        return status_map[stage]
    
    def _set_stage_status(self, workflow: WorkflowState, stage: EditingStage, status: StageStatus):
        """Set status of a specific stage"""
        if stage == EditingStage.ACQUISITIONS:
            workflow.acquisitions_status = status
        elif stage == EditingStage.DEVELOPMENTAL:
            workflow.developmental_status = status
        elif stage == EditingStage.LINE:
            workflow.line_status = status
        elif stage == EditingStage.COPY:
            workflow.copy_status = status
        elif stage == EditingStage.PROOF:
            workflow.proof_status = status
        elif stage == EditingStage.COLD_READ:
            workflow.cold_read_status = status
    
    def _get_next_stage(self, current_stage: EditingStage) -> Optional[EditingStage]:
        """Get the next stage in sequence"""
        try:
            current_index = self.STAGE_ORDER.index(current_stage)
            if current_index < len(self.STAGE_ORDER) - 1:
                return self.STAGE_ORDER[current_index + 1]
        except ValueError:
            pass
        return None
    
    def generate_workflow_report(self, manuscript_id: str) -> dict:
        """
        Generate a summary report of the workflow.
        
        Returns:
            Dictionary with workflow statistics
        """
        if manuscript_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[manuscript_id]
        
        # Calculate duration
        duration = None
        if workflow.started_at and workflow.completed_at:
            duration = (workflow.completed_at - workflow.started_at).total_seconds() / 3600  # hours
        
        return {
            "manuscript_id": manuscript_id,
            "status": "complete" if workflow.completed_at else "in_progress",
            "current_stage": workflow.current_stage.value if workflow.current_stage else None,
            "stages": {
                "acquisitions": workflow.acquisitions_status.value,
                "developmental": workflow.developmental_status.value,
                "line": workflow.line_status.value,
                "copy": workflow.copy_status.value,
                "proof": workflow.proof_status.value,
                "cold_read": workflow.cold_read_status.value
            },
            "total_issues_found": workflow.total_issues_found,
            "total_fixes_applied": workflow.total_fixes_applied,
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "duration_hours": round(duration, 2) if duration else None
        }
