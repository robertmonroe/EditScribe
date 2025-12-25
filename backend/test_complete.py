"""
Test script for all review agents including new ones
"""

import sys
sys.path.append('.')

from core.llm_client import LLMClient
from agents.series_bible_manager import SeriesBibleManager
from agents.consistency_agent import ConsistencyAgent
from agents.developmental_agent import DevelopmentalReviewAgent
from agents.grammar_agent import GrammarAgent
from agents.prose_quality_agent import ProseQualityAgent
from agents.proofreading_agent import ProofreadingAgent
from agents.selective_editor_agent import SelectiveEditorAgent


SAMPLE_MANUSCRIPT = """
# Chapter 1

Detective Sarah Martinez, 28, walked into the precinct. Her blue eyes scanned the room.

"Morning," said her partner Mike Chen, 35.

Sarah hung up her red wool coat.

She was angry about the case. She felt frustrated.

# Chapter 10

On Wednesday, October 18th, Sarah pulled her blue coat tighter. Her brown eyes looked tired.

Mike, now 36, handed her coffee. "We need to talk," he said quietly.
"""


def main():
    print("=" * 60)
    print("EditScribe - Complete Review Pipeline Test")
    print("=" * 60)
    
    llm_client = LLMClient()
    
    # 1. Extract Bible
    print("\n1. Extracting Series Bible...")
    bible_manager = SeriesBibleManager(llm_client)
    bible = bible_manager.execute(SAMPLE_MANUSCRIPT, "test_003")
    print(f"   Characters: {[c.name for c in bible.characters]}")
    
    all_issues = []
    
    # 2. Run Consistency Agent
    print("\n2. Running Consistency Agent...")
    consistency_agent = ConsistencyAgent(llm_client)
    consistency_issues = consistency_agent.execute(SAMPLE_MANUSCRIPT, bible)
    all_issues.extend(consistency_issues)
    print(f"   Found {len(consistency_issues)} consistency issues")
    
    # 3. Run Developmental Agent
    print("\n3. Running Developmental Agent...")
    dev_agent = DevelopmentalReviewAgent(llm_client)
    dev_issues = dev_agent.execute(SAMPLE_MANUSCRIPT, bible)
    all_issues.extend(dev_issues)
    print(f"   Found {len(dev_issues)} developmental issues")
    
    # 4. Run Prose Quality Agent
    print("\n4. Running Prose Quality Agent...")
    prose_agent = ProseQualityAgent(llm_client)
    prose_issues = prose_agent.execute(SAMPLE_MANUSCRIPT)
    all_issues.extend(prose_issues)
    print(f"   Found {len(prose_issues)} prose quality issues")
    
    # 5. Run Grammar Agent
    print("\n5. Running Grammar Agent...")
    grammar_agent = GrammarAgent(llm_client)
    grammar_issues = grammar_agent.execute(SAMPLE_MANUSCRIPT)
    all_issues.extend(grammar_issues)
    print(f"   Found {len(grammar_issues)} grammar issues")
    
    # 6. Run Proofreading Agent
    print("\n6. Running Proofreading Agent...")
    proof_agent = ProofreadingAgent(llm_client)
    proof_issues = proof_agent.execute(SAMPLE_MANUSCRIPT)
    all_issues.extend(proof_issues)
    print(f"   Found {len(proof_issues)} proofreading issues")
    
    # Display all issues
    print(f"\n{'=' * 60}")
    print(f"ALL ISSUES FOUND ({len(all_issues)} total):")
    print(f"{'=' * 60}\n")
    
    for issue in all_issues:
        print(f"{issue}")
        print(f"  Location: {issue.location}")
        print(f"  Suggestion: {issue.suggestion}")
        print()
    
    # 7. Test Selective Editor (apply first 3 issues)
    if len(all_issues) > 0:
        print(f"\n7. Testing Selective Editor...")
        print(f"   Applying first {min(3, len(all_issues))} fixes...")
        
        editor = SelectiveEditorAgent(llm_client)
        result = editor.execute(SAMPLE_MANUSCRIPT, all_issues[:3])
        
        print(f"\n   ✅ Applied {result['fixes_applied']} of {result['fixes_requested']} fixes")
        print(f"\n   Change Log:")
        for change in result['change_log']:
            print(f"   - Issue #{change['issue_id']}: {change['description']}")
            print(f"     Before: {change['before'][:50]}...")
            print(f"     After:  {change['after'][:50]}...")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Issues: {len(all_issues)}")
    print(f"  - Consistency (Bible conflicts): {len(consistency_issues)}")
    print(f"  - Developmental: {len(dev_issues)}")
    print(f"  - Prose Quality: {len(prose_issues)}")
    print(f"  - Grammar: {len(grammar_issues)}")
    print(f"  - Proofreading: {len(proof_issues)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
