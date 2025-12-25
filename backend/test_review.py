"""
Test script for review agents
"""

import sys
sys.path.append('.')

from core.llm_client import LLMClient
from agents.series_bible_manager import SeriesBibleManager
from agents.consistency_agent import ConsistencyAgent
from agents.developmental_agent import DevelopmentalReviewAgent
from agents.grammar_agent import GrammarAgent


SAMPLE_MANUSCRIPT = """
# Chapter 1

Detective Sarah Martinez, 28, walked into the precinct. Her blue eyes scanned the room.

"Morning," said her partner Mike Chen, 35.

Sarah hung up her red wool coat.

# Chapter 10

On Wednesday, October 18th, Sarah pulled her blue coat tighter. Her brown eyes looked tired.

Mike, now 36, handed her coffee.
"""


def main():
    print("=" * 60)
    print("EditScribe - Review Agents Test")
    print("=" * 60)
    
    llm_client = LLMClient()
    
    # 1. Extract Bible
    print("\n1. Extracting Series Bible...")
    bible_manager = SeriesBibleManager(llm_client)
    bible = bible_manager.execute(SAMPLE_MANUSCRIPT, "test_002")
    
    print(f"   Characters: {[c.name for c in bible.characters]}")
    
    # 2. Run Consistency Agent
    print("\n2. Running Consistency Agent...")
    consistency_agent = ConsistencyAgent(llm_client)
    consistency_issues = consistency_agent.execute(SAMPLE_MANUSCRIPT, bible)
    
    print(f"\n   Found {len(consistency_issues)} consistency issues:")
    for issue in consistency_issues:
        print(f"   {issue}")
    
    # 3. Run Developmental Agent
    print("\n3. Running Developmental Agent...")
    dev_agent = DevelopmentalReviewAgent(llm_client)
    dev_issues = dev_agent.execute(SAMPLE_MANUSCRIPT, bible)
    
    print(f"\n   Found {len(dev_issues)} developmental issues:")
    for issue in dev_issues:
        print(f"   {issue}")
    
    # 4. Run Grammar Agent
    print("\n4. Running Grammar Agent...")
    grammar_agent = GrammarAgent(llm_client)
    grammar_issues = grammar_agent.execute(SAMPLE_MANUSCRIPT)
    
    print(f"\n   Found {len(grammar_issues)} grammar issues:")
    for issue in grammar_issues:
        print(f"   {issue}")
    
    # Summary
    total = len(consistency_issues) + len(dev_issues) + len(grammar_issues)
    print(f"\n{'=' * 60}")
    print(f"TOTAL ISSUES FOUND: {total}")
    print(f"  - Consistency (Bible conflicts): {len(consistency_issues)}")
    print(f"  - Developmental: {len(dev_issues)}")
    print(f"  - Grammar: {len(grammar_issues)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
