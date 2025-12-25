"""
Test Cold Reader integration and sequential workflow enforcement
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.managing_editor import ManagingEditor, EditingStage, StageStatus
from core.llm_client import LLMClient
from core.style_sheet import StyleSheet
from agents.cold_reader import ColdReader


def test_cold_reader_sequential_enforcement():
    """Test that Cold Reader cannot run before Proofreader is complete"""
    print("\n=== Testing Sequential Enforcement ===")
    
    managing_editor = ManagingEditor()
    manuscript_id = "test_manuscript_001"
    
    # Start workflow
    workflow = managing_editor.start_workflow(manuscript_id)
    print(f"✓ Workflow started, current stage: {workflow.current_stage.value}")
    
    # Try to run Cold Read immediately (should fail)
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.COLD_READ)
    print(f"\n✓ Attempting Cold Read at start: {can_run}")
    print(f"  Reason: {reason}")
    assert not can_run, "Cold Read should not be allowed before previous stages"
    assert "Must complete" in reason, f"Expected blocking message, got: {reason}"
    
    # Complete all previous stages
    stages_to_complete = [
        EditingStage.ACQUISITIONS,
        EditingStage.DEVELOPMENTAL,
        EditingStage.LINE,
        EditingStage.COPY,
        EditingStage.PROOF
    ]
    
    for stage in stages_to_complete:
        workflow = managing_editor.mark_stage_complete(manuscript_id, stage, issues_found=0)
        print(f"✓ Completed {stage.value}, next: {workflow.current_stage.value if workflow.current_stage else 'None'}")
    
    # Now Cold Read should be available
    can_run, reason = managing_editor.can_run_stage(manuscript_id, EditingStage.COLD_READ)
    print(f"\n✓ Attempting Cold Read after all stages: {can_run}")
    print(f"  Reason: {reason}")
    assert can_run, f"Cold Read should be allowed after all previous stages. Reason: {reason}"
    
    print("\n✅ Sequential enforcement test PASSED")


def test_cold_reader_agent_execution():
    """Test that Cold Reader agent can process text"""
    print("\n=== Testing Cold Reader Agent ===")
    
    # Sample manuscript text
    test_manuscript = """
    Chapter 1
    
    John walked into the room. He saw her standing there. She looked at him.
    "What are you doing here?" she asked.
    "I came to find you," he said.
    They stood in silence for a moment.
    
    Chapter 2
    
    The next day, Sarah went to the office. Her boss was waiting for her.
    "We need to talk," he said ominously.
    She felt a knot form in her stomach. What could this be about?
    """
    
    style_sheet = StyleSheet(
        manuscript_id="test_001",
        title="Test Novel",
        genre="Mystery",
        word_count=100
    )
    
    try:
        llm_client = LLMClient()
        agent = ColdReader(llm_client)
        
        print("✓ Cold Reader agent initialized")
        print("✓ Running agent execution (this will call LLM)...")
        
        result = agent.execute(test_manuscript, style_sheet)
        
        print(f"\n✓ Agent execution complete")
        print(f"  Reader Report length: {len(result.get('reader_report', ''))} characters")
        print(f"  Total issues found: {result.get('total_issues', 0)}")
        print(f"  Issues returned: {len(result.get('issues', []))}")
        
        # Verify result structure
        assert "reader_report" in result, "Result should contain reader_report"
        assert "total_issues" in result, "Result should contain total_issues"
        assert "issues" in result, "Result should contain issues list"
        
        print("\n✅ Cold Reader agent test PASSED")
        
        # Print sample of reader report
        if result.get('reader_report'):
            print("\n--- Sample Reader Report (first 300 chars) ---")
            print(result['reader_report'][:300] + "...")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Cold Reader agent test FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_workflow_completion():
    """Test that workflow completes after Cold Read"""
    print("\n=== Testing Workflow Completion ===")
    
    managing_editor = ManagingEditor()
    manuscript_id = "test_manuscript_002"
    
    # Start and complete all stages
    workflow = managing_editor.start_workflow(manuscript_id)
    
    all_stages = [
        EditingStage.ACQUISITIONS,
        EditingStage.DEVELOPMENTAL,
        EditingStage.LINE,
        EditingStage.COPY,
        EditingStage.PROOF,
        EditingStage.COLD_READ
    ]
    
    for stage in all_stages:
        workflow = managing_editor.mark_stage_complete(manuscript_id, stage, issues_found=0)
    
    # Check workflow is complete
    assert workflow.completed_at is not None, "Workflow should be marked complete"
    assert workflow.current_stage is None, "Current stage should be None when complete"
    
    print(f"✓ Workflow completed at: {workflow.completed_at}")
    print(f"✓ Current stage: {workflow.current_stage}")
    
    print("\n✅ Workflow completion test PASSED")


if __name__ == "__main__":
    print("="*60)
    print("COLD READER INTEGRATION TESTS")
    print("="*60)
    
    try:
        # Test 1: Sequential enforcement
        test_cold_reader_sequential_enforcement()
        
        # Test 2: Agent execution
        test_cold_reader_agent_execution()
        
        # Test 3: Workflow completion
        test_workflow_completion()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("TESTS FAILED ❌")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
