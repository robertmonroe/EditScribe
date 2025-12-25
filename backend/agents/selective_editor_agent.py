"""
Selective Editor Agent - applies user-selected fixes to manuscript
Uses Claude Sonnet 4.5 to preserve author's voice while fixing issues
"""

from typing import List, Dict
from agents.base import Agent
from core.issue import Issue
from core.llm_client import LLMClient
import re


class SelectiveEditorAgent(Agent):
    """
    Applies only user-selected fixes to the manuscript.
    Preserves author's voice and style while fixing specific issues.
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("selective_editor", llm_client)
    
    def execute(
        self,
        manuscript_text: str,
        selected_issues: List[Issue]
    ) -> Dict[str, any]:
        """
        Apply selected fixes to manuscript.
        
        Args:
            manuscript_text: Original manuscript
            selected_issues: List of issues user wants to fix
            
        Returns:
            Dictionary with edited_text and change_log
        """
        print(f"✏️ Applying {len(selected_issues)} selected fixes...")
        
        edited_text = manuscript_text
        change_log = []
        
        # Group issues by severity for processing order
        critical_issues = [i for i in selected_issues if i.severity == "critical"]
        major_issues = [i for i in selected_issues if i.severity == "major"]
        minor_issues = [i for i in selected_issues if i.severity == "minor"]
        
        # Process in order: critical → major → minor
        for issue in critical_issues + major_issues + minor_issues:
            result = self._apply_fix(edited_text, issue)
            if result["success"]:
                edited_text = result["edited_text"]
                change_log.append({
                    "issue_id": issue.id,
                    "description": issue.description,
                    "before": result["before"],
                    "after": result["after"]
                })
        
        print(f"✅ Applied {len(change_log)} fixes successfully")
        
        return {
            "edited_text": edited_text,
            "change_log": change_log,
            "fixes_applied": len(change_log),
            "fixes_requested": len(selected_issues)
        }
    
    def _apply_fix(self, text: str, issue: Issue) -> Dict[str, any]:
        """Apply a single fix"""
        
        # For Bible conflicts, use direct replacement if possible
        if issue.bible_conflict:
            return self._apply_bible_fix(text, issue)
        
        # For other issues, use LLM to apply fix while preserving voice
        return self._apply_llm_fix(text, issue)
    
    def _apply_bible_fix(self, text: str, issue: Issue) -> Dict[str, any]:
        """Apply a Bible conflict fix (direct replacement)"""
        
        # Try to use original_text if available
        if hasattr(issue, 'original_text') and issue.original_text and issue.original_text in text:
             # If the suggestion is a direct replacement (short), use it
             if len(issue.suggestion) < 50 and "Change to" in issue.suggestion:
                 # Extract the new text from "Change to 'new text'"
                 match = re.search(r"Change to:? ['\"](.*?)['\"]", issue.suggestion)
                 if match:
                     new_text = match.group(1)
                     edited_text = text.replace(issue.original_text, new_text, 1)
                     return {
                         "success": True,
                         "edited_text": edited_text,
                         "before": issue.original_text,
                         "after": new_text
                     }
        
        # Fallback to LLM if direct replacement fails
        return self._apply_llm_fix(text, issue)
    
    def _apply_llm_fix(self, text: str, issue: Issue) -> Dict[str, any]:
        """Use LLM to apply fix while preserving voice"""
        
        # 1. Identify the section to replace
        target_text = issue.original_text if hasattr(issue, 'original_text') and issue.original_text else None
        
        section = ""
        if target_text and target_text in text:
            # Use context around the original text
            idx = text.find(target_text)
            start = max(0, idx - 200)
            end = min(len(text), idx + len(target_text) + 200)
            section = text[start:end]
        else:
            # Fallback to location hint
            section = self._extract_section(text, issue.location)
            
        if not section:
            return {"success": False, "edited_text": text, "before": "", "after": ""}
        
        prompt = f"""You are a professional editor. Fix the issue described below in the provided text segment.

ISSUE: {issue.description}
SUGGESTION: {issue.suggestion}
TARGET TEXT: "{target_text}"

CONTEXT SEGMENT:
{section}

INSTRUCTIONS:
1. Rewrite the CONTEXT SEGMENT to fix the issue.
2. Preserve the author's voice and style.
3. Make ONLY the necessary changes.
4. Return ONLY the rewritten segment. Do not include "Here is the fix" or quotes.
"""

        try:
            corrected_section = self.generate(prompt, max_tokens=1000, temperature=0.3)
            
            # Clean up response
            corrected_section = corrected_section.strip()
            if corrected_section.startswith('"') and corrected_section.endswith('"'):
                corrected_section = corrected_section[1:-1]
            
            # Replace the section in the full text
            # We replace the *entire context section* with the *rewritten context section*
            # This is safer than trying to find the small target text again
            edited_text = text.replace(section, corrected_section, 1)
            
            return {
                "success": True,
                "edited_text": edited_text,
                "before": section,
                "after": corrected_section
            }
        except Exception as e:
            print(f"⚠️ Fix failed: {e}")
            return {"success": False, "edited_text": text, "before": "", "after": ""}
    
    def _extract_section(self, text: str, location: str) -> str:
        """Extract relevant section based on location hint"""
        # Fallback if original_text is missing
        words = text.split()
        mid_point = len(words) // 2
        start = max(0, mid_point - 250)
        end = min(len(words), mid_point + 250)
        return " ".join(words[start:end])
