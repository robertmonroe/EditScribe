"""
Line Editor - Prose Polishing
Third stage in professional publishing workflow
"""

from typing import List
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.issue import Issue
from core.llm_client import LLMClient


class LineEditor(Agent):
    """
    Line Editor - Prose Polishing
    
    This is the THIRD agent in the professional workflow.
    Only runs AFTER Developmental Editor completes.
    
    Function: Polish prose at the sentence level.
    Fix wordiness, awkward phrasing, syntax, voice.
    
    Deliverables:
    - Line Edit (sentence-level rewrites using Track Changes)
    - Voice consistency analysis
    - Tone improvements
    
    Uses: Claude Sonnet 4 (balanced - creative but precise)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("line", llm_client)
        self.issue_counter = 0
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> List[Issue]:
        """
        Perform line edit.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet
            
        Returns:
            List of prose issues
        """
        print(f"✍️  Line Editor: Polishing prose...")
        print(f"   Manuscript length: {len(manuscript_text)} characters")
        
        issues = []
        
        # Chunk the manuscript to handle large texts
        chunk_size = 50000
        chunks = [manuscript_text[i:i+chunk_size] for i in range(0, len(manuscript_text), chunk_size)]
        
        print(f"   Processing {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            print(f"   - Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            
            # Analyze voice and tone
            voice_issues = self._analyze_voice(chunk)
            print(f"      Voice issues found: {len(voice_issues)}")
            issues.extend(voice_issues)
            
            # Find wordiness
            word_issues = self._find_wordiness(chunk)
            print(f"      Wordiness issues found: {len(word_issues)}")
            issues.extend(word_issues)
            
            # Find awkward phrasing
            awkward_issues = self._find_awkward_phrasing(chunk)
            print(f"      Awkward phrasing issues found: {len(awkward_issues)}")
            issues.extend(awkward_issues)
        
        print(f"✅ Line Editor: Found {len(issues)} prose issues TOTAL")
        
        return issues
    
    def _analyze_voice(self, text: str) -> List[Issue]:
        """Analyze voice consistency"""
        issues = []
        
        prompt = f"""You are a Line Editor analyzing VOICE and TONE.

MANUSCRIPT:
{text}

Identify voice/tone problems:
- Inconsistent narrative voice
- Tone shifts (serious to comedic without reason)
- Weak or unclear authorial voice
- POV slips

Return JSON array with this EXACT structure:
[
  {{
    "severity": "minor",
    "location": "Chapter 1, paragraph 3",
    "quote": "He thought she looked nice.",
    "description": "POV slip from third-person limited to omniscient",
    "suggestion": "Show his reaction through action instead of direct thought"
  }}
]

CRITICAL RULES:
1. Include the ACTUAL text causing the issue in "quote"
2. Include actual "description" text explaining the problem
3. Include actual "suggestion" text with how to fix it
4. If no issues found, return: []
"""
        
        try:
            print(f"      🔍 Calling LLM for voice analysis...")
            response = self.generate(prompt, max_tokens=4000, temperature=0.3)
            print(f"      📝 LLM Response length: {len(response)} chars")
            print(f"      📝 LLM Response (first 300 chars): {response[:300]}")
            
            voice_issues = self.parse_json_response(response)
            print(f"      ✅ Parsed {len(voice_issues)} voice issues from JSON")
            
            for issue_data in voice_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="line",
                    severity=issue_data.get("severity", "minor"),
                    category="voice",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Voice/tone issue"),
                    suggestion=issue_data.get("suggestion", "Review and revise"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"      ⚠️  Failed to analyze voice: {e}")
            import traceback
            traceback.print_exc()
        
        return issues
    
    def _find_wordiness(self, text: str) -> List[Issue]:
        """Find wordy passages"""
        issues = []
        
        prompt = f"""You are a Line Editor finding WORDINESS.

MANUSCRIPT:
{text}

Identify wordy passages:
- Redundant phrases ("past history", "future plans")
- Overwriting (using 20 words when 10 would do)
- Weak verbs with adverbs ("walked quickly" vs "strode")
- Passive voice where active is better

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 1, opening paragraph",
    "quote": "The elevator descended down in a smooth, expensive silence that was characteristic of German engineering",
    "description": "Wordy phrase / Redundant 'descended down'",
    "suggestion": "The elevator descended in the smooth silence of German engineering"
  }}
]

CRITICAL RULES:
1. Include the ACTUAL wordy text in "quote"
2. Include the REWRITTEN tighter version in "suggestion"
3. If no issues found, return: []
"""
        
        try:
            print(f"      🔍 Calling LLM for wordiness analysis...")
            response = self.generate(prompt, max_tokens=4000, temperature=0.3)
            print(f"      📝 LLM Response length: {len(response)} chars")
            
            wordiness_issues = self.parse_json_response(response)
            print(f"      ✅ Parsed {len(wordiness_issues)} wordiness issues from JSON")
            
            for issue_data in wordiness_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="line",
                    severity="minor",
                    category="wordiness",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Wordy passage"),
                    suggestion=issue_data.get("suggestion", "Tighten prose"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"      ⚠️  Failed to find wordiness: {e}")
            import traceback
            traceback.print_exc()
        
        return issues
    
    def _find_awkward_phrasing(self, text: str) -> List[Issue]:
        """Find awkward phrasing"""
        issues = []
        
        prompt = f"""You are a Line Editor finding AWKWARD PHRASING.

MANUSCRIPT:
{text}

Identify awkward sentences:
- Unclear syntax
- Confusing sentence structure
- Clunky transitions
- Repetitive sentence patterns

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 1, paragraph 5",
    "quote": "The room was filled with a bluish light that had a pallor that reminded Max of a morgue",
    "description": "Awkward phrasing / Repetitive 'that'",
    "suggestion": "The room's bluish pallor reminded Max of a morgue"
  }}
]

CRITICAL RULES:
1. Include the ACTUAL awkward text in "quote"
2. Include the REVISED smoother version in "suggestion"
3. If no issues found, return: []
"""
        
        try:
            print(f"      🔍 Calling LLM for awkward phrasing analysis...")
            response = self.generate(prompt, max_tokens=4000, temperature=0.3)
            print(f"      📝 LLM Response length: {len(response)} chars")
            
            awkward_issues = self.parse_json_response(response)
            print(f"      ✅ Parsed {len(awkward_issues)} awkward phrasing issues from JSON")
            
            for issue_data in awkward_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="line",
                    severity="minor",
                    category="syntax",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Awkward phrasing"),
                    suggestion=issue_data.get("suggestion", "Revise for clarity"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"      ⚠️  Failed to find awkward phrasing: {e}")
            import traceback
            traceback.print_exc()
        
        return issues
