"""
Cold Reader - Fresh Eyes Review
Sixth (optional) stage in professional publishing workflow
"""

from typing import List, Dict
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.issue import Issue
from core.llm_client import LLMClient


class ColdReader(Agent):
    """
    Cold Reader - Fresh Eyes Review
    
    This is the SIXTH (optional) agent in the professional workflow.
    Only runs AFTER Proofreader completes.
    
    Function: Provide a reader's perspective on the near-final manuscript.
    Flag areas where readers might get confused, bored, or lose clarity.
    
    Deliverables:
    - Reader Report (overall impressions)
    - Confusion points
    - Pacing feedback
    - Engagement issues
    
    Uses: Gemini 2.5 Flash (budget - reader perspective doesn't need premium)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("cold_read", llm_client)
        self.issue_counter = 0
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> Dict:
        """
        Perform cold read review.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet
            
        Returns:
            Dictionary with reader report and specific issues
        """
        print(f"👀 Cold Reader: Providing fresh eyes review...")
        
        # Generate overall reader report
        reader_report = self._generate_reader_report(manuscript_text, style_sheet)
        
        # Find specific confusion points
        confusion_issues = self._find_confusion_points(manuscript_text)
        
        # Find pacing/boredom issues
        pacing_issues = self._find_pacing_issues(manuscript_text)
        
        all_issues = confusion_issues + pacing_issues
        
        print(f"✅ Cold Reader: Found {len(all_issues)} reader experience issues")
        
        return {
            "reader_report": reader_report,
            "total_issues": len(all_issues),
            "issues": [issue.to_dict() for issue in all_issues]
        }
    
    def _generate_reader_report(self, text: str, style_sheet: StyleSheet) -> str:
        """Generate overall reader impression report"""
        
        prompt = f"""You are a professional Cold Reader providing fresh eyes feedback on a near-final manuscript.

MANUSCRIPT DETAILS:
- Title: {style_sheet.title or "Untitled"}
- Genre: {style_sheet.genre or "Unknown"}
- Word Count: {style_sheet.word_count:,} words

MANUSCRIPT TEXT:
{text}

Write a Reader Report (500-800 words) from the perspective of a typical reader in the target audience.

STRUCTURE:
1. **First Impressions**: What grabbed you? What didn't?
2. **Engagement**: Where did you feel hooked? Where did you lose interest?
3. **Clarity**: Were there confusing moments? Did you have to reread anything?
4. **Emotional Impact**: What did you feel? Did the story resonate?
5. **Overall Recommendation**: Would you recommend this to a friend?

TONE: Honest, constructive, reader-focused (not literary criticism).
"""
        
        return self.generate(prompt, max_tokens=2000, temperature=0.7)
    
    def _find_confusion_points(self, text: str) -> List[Issue]:
        """Find points where readers might get confused"""
        issues = []
        
        # Chunk the manuscript
        chunk_size = 50000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        print(f"   Analyzing {len(chunks)} chunks for confusion points...")
        
        for i, chunk in enumerate(chunks):
            prompt = f"""You are a Cold Reader identifying CONFUSION POINTS.

MANUSCRIPT:
{chunk}

Find areas where a typical reader might get confused:
- Unclear character motivations
- Confusing scene transitions
- Ambiguous pronouns ("he" - which he?)
- Missing context or setup
- Unclear time jumps

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 2, Scene 3",
    "quote": "He walked into the room she had left",
    "description": "Confusing - unclear which 'she' is being referenced, multiple female characters in prior scene",
    "suggestion": "Clarify with character name: 'He walked into the room Sarah had left'"
  }}
]

CRITICAL RULES:
1. Include the CONFUSING text in "quote"
2. Explain WHY it's confusing
3. Suggest how to clarify
4. If no confusion found, return: []
"""
            
            try:
                response = self.generate(prompt, max_tokens=4000, temperature=0.3)
                confusion_data = self.parse_json_response(response)
                
                for issue_data in confusion_data:
                    self.issue_counter += 1
                    issues.append(Issue(
                        id=self.issue_counter,
                        stage="cold_read",
                        severity="minor",
                        category="clarity",
                        location=issue_data.get("location", "Unknown"),
                        original_text=issue_data.get("quote", ""),
                        description=issue_data.get("description", "Reader confusion point"),
                        suggestion=issue_data.get("suggestion", "Improve clarity"),
                        bible_conflict=False
                    ))
            except Exception as e:
                print(f"⚠️  Failed to analyze confusion in chunk {i+1}: {e}")
        
        return issues
    
    def _find_pacing_issues(self, text: str) -> List[Issue]:
        """Find pacing and engagement issues"""
        issues = []
        
        # Chunk the manuscript
        chunk_size = 50000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        print(f"   Analyzing {len(chunks)} chunks for pacing issues...")
        
        for i, chunk in enumerate(chunks):
            prompt = f"""You are a Cold Reader identifying PACING and ENGAGEMENT issues.

MANUSCRIPT:
{chunk}

Find areas where a typical reader might lose interest:
- Scenes that drag or feel slow
- Repetitive information
- Lack of tension or stakes
- Info dumps that bog down the narrative
- Sections where you wanted to skip ahead

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 5, middle section",
    "quote": "[First few sentences of the slow section]",
    "description": "Pacing issue: Extended description of the building's architecture slows momentum right after a tense scene",
    "suggestion": "Cut or condense the architectural details, maintain tension from previous scene"
  }}
]

CRITICAL RULES:
1. Include the START of the slow section in "quote"
2. Explain the pacing problem
3. Suggest how to improve
4. If no issues found, return: []
"""
            
            try:
                response = self.generate(prompt, max_tokens=4000, temperature=0.3)
                pacing_data = self.parse_json_response(response)
                
                for issue_data in pacing_data:
                    self.issue_counter += 1
                    issues.append(Issue(
                        id=self.issue_counter,
                        stage="cold_read",
                        severity="minor",
                        category="pacing",
                        location=issue_data.get("location", "Unknown"),
                        original_text=issue_data.get("quote", ""),
                        description=issue_data.get("description", "Pacing issue"),
                        suggestion=issue_data.get("suggestion", "Improve pacing"),
                        bible_conflict=False
                    ))
            except Exception as e:
                print(f"⚠️  Failed to analyze pacing in chunk {i+1}: {e}")
        
        return issues
