"""
Developmental Review Agent - checks plot, character arcs, pacing
Uses Claude Sonnet 4.5 for complex story analysis
"""

from typing import List
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.issue import Issue
from core.llm_client import LLMClient
import json


class DevelopmentalEditor(Agent):
    """
    Reviews big-picture story elements:
    - Plot structure and logic
    - Character development and arcs
    - Pacing and tension
    - Theme consistency
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("developmental", llm_client)
        self.issue_counter = 0
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> List[Issue]:
        """
        Review manuscript for developmental issues.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet for context
            
        Returns:
            List of developmental issues
        """
        print(f"📖 Running developmental review...")
        
        # Build character context from Style Sheet
        char_context = "\n".join([
            f"- {c.name}: {c.occupation}, {c.personality_traits}"
            for c in style_sheet.characters
        ])
        
        prompt = f"""You are a professional developmental editor. Review this manuscript for BIG-PICTURE issues.

CHARACTERS (from Style Sheet):
{char_context}

MANUSCRIPT:
{manuscript_text}

Find issues with:
1. **Plot**: Plot holes, logic gaps, missing motivation
2. **Character Arcs**: Lack of growth, inconsistent behavior
3. **Pacing**: Sections that drag or rush
4. **Structure**: Chapter organization, scene flow

Return ONLY a JSON array of issues:
[
  {{
    "severity": "major",
    "category": "plot",
    "location": "Chapter 3",
    "quote": "She walked into the room.",
    "description": "Plot hole: Sarah's motivation unclear",
    "suggestion": "Add scene showing her backstory"
  }}
]

Focus on MAJOR issues only. Return [] if none found."""

        response = self.generate(prompt, max_tokens=4000, temperature=0.3)
        
        issues = []
        try:
            issues_data = self.parse_json_response(response)
            
            for issue_data in issues_data:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="developmental",
                    severity=issue_data.get("severity", "major"),
                    category=issue_data.get("category", "plot"),
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", ""),
                    suggestion=issue_data.get("suggestion", ""),
                    bible_conflict=False
                ))
        except:
            pass
        
        print(f"✅ Found {len(issues)} developmental issues")
        return issues
