"""
Multi-Stage Review Manager for EditScribe
Orchestrates all review agents to analyze manuscripts
"""

import asyncio
from typing import List, Dict, Any
from pathlib import Path
import json

from agents.consistency_agent import ConsistencyAgent
from agents.developmental_agent import DevelopmentalReviewAgent
from agents.grammar_agent import GrammarAgent
from agents.prose_quality_agent import ProseQualityAgent
from agents.proofreading_agent import ProofreadingAgent
from core.models import SeriesBible
from core.issue import Issue
from core.llm_client import LLMClient


class MultiStageReviewManager:
    """Manages the multi-stage manuscript review process"""
    
    def __init__(self):
        llm_client = LLMClient()
        self.consistency_agent = ConsistencyAgent(llm_client)
        self.developmental_agent = DevelopmentalReviewAgent(llm_client)
        self.grammar_agent = GrammarAgent(llm_client)
        self.prose_agent = ProseQualityAgent(llm_client)
        self.proofreading_agent = ProofreadingAgent(llm_client)
    
    async def review_manuscript(
        self,
        manuscript_text: str,
        bible: SeriesBible,
        manuscript_id: str
    ) -> Dict[str, Any]:
        """
        Run all review agents on the manuscript.
        
        Args:
            manuscript_text: Full manuscript text
            bible: Series Bible for consistency checking
            manuscript_id: Unique manuscript identifier
            
        Returns:
            Dictionary with all issues found by all agents
        """
        print(f"\n🔍 Starting multi-stage review for manuscript {manuscript_id}")
        
        all_issues = []
        agent_results = {}
        
        # Stage 1: Consistency Check (uses Bible)
        print("\n📖 Stage 1: Checking consistency against Series Bible...")
        consistency_issues = self.consistency_agent.execute(manuscript_text, bible)
        all_issues.extend(consistency_issues)
        agent_results['consistency'] = {
            'count': len(consistency_issues),
            'issues': [self._issue_to_dict(i) for i in consistency_issues]
        }
        print(f"   Found {len(consistency_issues)} consistency issues")
        
        # Stage 2: Developmental Review
        print("\n📚 Stage 2: Analyzing story development...")
        developmental_issues = self.developmental_agent.execute(manuscript_text, bible)
        all_issues.extend(developmental_issues)
        agent_results['developmental'] = {
            'count': len(developmental_issues),
            'issues': [self._issue_to_dict(i) for i in developmental_issues]
        }
        print(f"   Found {len(developmental_issues)} developmental issues")
        
        # Stage 3: Prose Quality
        print("\n✍️  Stage 3: Evaluating prose quality...")
        prose_issues = self.prose_agent.execute(manuscript_text, bible)
        all_issues.extend(prose_issues)
        agent_results['prose'] = {
            'count': len(prose_issues),
            'issues': [self._issue_to_dict(i) for i in prose_issues]
        }
        print(f"   Found {len(prose_issues)} prose quality issues")
        
        # Stage 4: Grammar Check
        print("\n📝 Stage 4: Checking grammar and mechanics...")
        grammar_issues = self.grammar_agent.execute(manuscript_text, bible)
        all_issues.extend(grammar_issues)
        agent_results['grammar'] = {
            'count': len(grammar_issues),
            'issues': [self._issue_to_dict(i) for i in grammar_issues]
        }
        print(f"   Found {len(grammar_issues)} grammar issues")
        
        # Stage 5: Final Proofreading
        print("\n🔎 Stage 5: Final proofreading pass...")
        proofreading_issues = self.proofreading_agent.execute(manuscript_text, bible)
        all_issues.extend(proofreading_issues)
        agent_results['proofreading'] = {
            'count': len(proofreading_issues),
            'issues': [self._issue_to_dict(i) for i in proofreading_issues]
        }
        print(f"   Found {len(proofreading_issues)} proofreading issues")
        
        # Calculate statistics
        total_issues = len(all_issues)
        bible_conflicts = len([i for i in all_issues if i.is_bible_conflict])
        
        # Categorize by severity
        critical = len([i for i in all_issues if i.severity == 'critical'])
        major = len([i for i in all_issues if i.severity == 'major'])
        minor = len([i for i in all_issues if i.severity == 'minor'])
        
        print(f"\n✅ Review complete!")
        print(f"   Total issues: {total_issues}")
        print(f"   Bible conflicts: {bible_conflicts}")
        print(f"   Critical: {critical}, Major: {major}, Minor: {minor}")
        
        return {
            'manuscript_id': manuscript_id,
            'total_issues': total_issues,
            'bible_conflicts': bible_conflicts,
            'severity_breakdown': {
                'critical': critical,
                'major': major,
                'minor': minor
            },
            'agent_results': agent_results,
            'all_issues': [self._issue_to_dict(i) for i in all_issues]
        }
    
    def _issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        """Convert Issue object to dictionary"""
        return {
            'type': issue.type,
            'severity': issue.severity,
            'chapter': issue.chapter,
            'paragraph': issue.paragraph,
            'line': issue.line,
            'original_text': issue.original_text,
            'suggestion': issue.suggestion,
            'explanation': issue.explanation,
            'is_bible_conflict': issue.is_bible_conflict
        }
