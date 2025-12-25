"""
Proofreader - Final Quality Control
Fifth stage in professional publishing workflow
"""

from typing import List
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.issue import Issue
from core.llm_client import LLMClient


class Proofreader(Agent):
    """
    Proofreader - Quality Control (QC)
    
    This is the FIFTH agent in the professional workflow.
    Only runs AFTER Copy Editor completes.
    
    Function: Final typo catch and formatting check.
    Looks at "First Pass Pages" for errors.
    
    Deliverables:
    - Master Proof (final sign-off)
    - Typo catches
    - Formatting checks
    
    Uses: Gemini 2.5 Flash (budget - simple QC)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("proof", llm_client)
        self.issue_counter = 0
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> List[Issue]:
        """
        Perform final proofread.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet
            
        Returns:
            List of typos and formatting issues
        """
        print(f"🔍 Proofreader: Final quality check...")
        
        issues = []
        
        # Chunk the manuscript
        chunk_size = 50000
        chunks = [manuscript_text[i:i+chunk_size] for i in range(0, len(manuscript_text), chunk_size)]
        
        print(f"   Processing {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            print(f"   - Chunk {i+1}/{len(chunks)}")
            
            # Find typos
            issues.extend(self._find_typos(chunk))
            
            # Check formatting
            issues.extend(self._check_formatting(chunk))
        
        print(f"✅ Proofreader: Found {len(issues)} final issues")
        
        return issues
    
    def _find_typos(self, text: str) -> List[Issue]:
        """Find typos and spelling errors"""
        issues = []
        
        prompt = f"""You are a Proofreader doing final TYPO CHECK.

MANUSCRIPT:
{text}

Find:
- Misspellings
- Repeated words ("the the")
- Missing words
- Transposed letters
- Homophones ("their" vs "there")

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 1, paragraph 3",
    "quote": "He recieved the letter",
    "description": "Typo: 'recieved' should be 'received' (i before e except after c)",
    "suggestion": "Change to: 'received'"
  }}
]

CRITICAL RULES:
1. Include the ACTUAL TYPO in "quote"
2. Show the CORRECT spelling
3. If no typos found, return: []
"""
        
        try:
            response = self.generate(prompt, max_tokens=4000, temperature=0.1)
            typo_issues = self.parse_json_response(response)
            
            for issue_data in typo_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="proof",
                    severity="minor",
                    category="typo",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Typo"),
                    suggestion=issue_data.get("suggestion", "Fix typo"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"⚠️  Failed to find typos: {e}")
        
        return issues
    
    def _check_formatting(self, text: str) -> List[Issue]:
        """Check formatting consistency"""
        issues = []
        
        prompt = f"""You are a Proofreader checking FORMATTING.

MANUSCRIPT:
{text}

Find formatting issues:
- Inconsistent paragraph spacing
- Missing scene breaks
- Inconsistent chapter headings
- Orphaned dialogue tags

Return JSON array with this EXACT structure:
[
  {{
    "location": "Between Chapter 2 and 3",
    "quote": "Chapter 3 [no break before]",
    "description": "Missing scene break - chapter transition is abrupt with no visual separator",
    "suggestion": "Add scene break marker (### or * * *)"
  }}
]

CRITICAL RULES:
1. Quote the FORMATTING ISSUE context in "quote"
2. Provide CONCRETE fix
3. If no issues found, return: []
"""
        
        try:
            response = self.generate(prompt, max_tokens=4000, temperature=0.1)
            format_issues = self.parse_json_response(response)
            
            for issue_data in format_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="proof",
                    severity="minor",
                    category="formatting",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Formatting issue"),
                    suggestion=issue_data.get("suggestion", "Fix formatting"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"⚠️  Failed to check formatting: {e}")
        
        return issues
