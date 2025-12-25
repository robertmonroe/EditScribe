"""
Copy Editor - Mechanical Perfection & Consistency
Fourth stage in professional publishing workflow
Merges old Consistency Agent + Grammar Agent
"""

from typing import List
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.issue import Issue
from core.llm_client import LLMClient


class CopyEditor(Agent):
    """
    Copy Editor - Mechanical Perfection & Consistency
    
    This is the FOURTH agent in the professional workflow.
    Only runs AFTER Line Editor completes.
    
    Function: Apply House Style (Chicago Manual).
    Guardian of the Style Sheet.
    
    Deliverables:
    - Copyedited manuscript
    - Updated Style Sheet
    - Grammar fixes
    - Consistency checks (timeline, character details)
    
    Uses: Gemini 2.5 Flash (budget - rule-based work)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("copy", llm_client)
        self.issue_counter = 0
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> List[Issue]:
        """
        Perform copyedit.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet
            
        Returns:
            List of mechanical and consistency issues
        """
        print(f"📝 Copy Editor: Checking grammar and consistency...")
        
        issues = []
        
        # Chunk the manuscript
        chunk_size = 50000
        chunks = [manuscript_text[i:i+chunk_size] for i in range(0, len(manuscript_text), chunk_size)]
        
        print(f"   Processing {len(chunks)} chunks...")
        
        for i, chunk in enumerate(chunks):
            print(f"   - Chunk {i+1}/{len(chunks)}")
            
            # Grammar and punctuation
            issues.extend(self._check_grammar(chunk))
            
            # Timeline consistency
            issues.extend(self._check_timeline(chunk, style_sheet))
            
            # Character consistency
            issues.extend(self._check_character_consistency(chunk, style_sheet))
            
            # House style compliance
            issues.extend(self._check_house_style(chunk, style_sheet))
        
        print(f"✅ Copy Editor: Found {len(issues)} mechanical issues")
        
        return issues
    
    def _check_grammar(self, text: str) -> List[Issue]:
        """Check grammar and punctuation"""
        issues = []
        
        prompt = f"""You are a Copy Editor checking GRAMMAR and PUNCTUATION.

MANUSCRIPT:
{text}

Identify errors:
- Subject-verb agreement
- Comma splices
- Sentence fragments
- Misplaced modifiers
- Pronoun agreement

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 1, paragraph 2",
    "quote": "The elevator descended... their footsteps was muffled",
    "description": "Subject-verb agreement error: plural subject 'footsteps' with singular verb 'was'",
    "suggestion": "Change to: 'their footsteps were muffled'"
  }}
]

CRITICAL RULES:
1. Include the ACTUAL ERROR in "quote"
2. Include the CORRECTED version in "suggestion"
3. If no errors found, return: []
"""
        
        try:
            response = self.generate(prompt, max_tokens=4000, temperature=0.1)
            grammar_issues = self.parse_json_response(response)
            
            for issue_data in grammar_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="copy",
                    severity="minor",
                    category="grammar",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Grammar error"),
                    suggestion=issue_data.get("suggestion", "Fix grammar"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"⚠️  Failed to check grammar: {e}")
        
        return issues
    
    def _check_timeline(self, text: str, style_sheet: StyleSheet) -> List[Issue]:
        """Check timeline consistency"""
        issues = []
        
        if not style_sheet.timeline:
            return issues
        
        timeline_str = "\n".join([f"- {e.date} ({e.day_of_week}): {e.event}" 
                                  for e in style_sheet.timeline[:10]])
        
        prompt = f"""You are a Copy Editor checking TIMELINE CONSISTENCY.

STYLE SHEET TIMELINE:
{timeline_str}

MANUSCRIPT:
{text}

Find timeline errors:
- Wrong day of week for a date
- Events out of chronological order
- Character aging inconsistencies
- Time passage errors

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 3",
    "quote": "It was Monday, March 15th",
    "description": "Timeline error: March 15th is actually a Wednesday according to the Style Sheet",
    "suggestion": "Change to 'Wednesday, March 15th' or adjust the date"
  }}
]

CRITICAL RULES:
1. Quote the ACTUAL ERROR from the manuscript in "quote"
2. Reference the Style Sheet timeline
3. If no errors found, return: []
"""
        
        try:
            response = self.generate(prompt, max_tokens=4000, temperature=0.1)
            timeline_issues = self.parse_json_response(response)
            
            for issue_data in timeline_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="copy",
                    severity="major",
                    category="timeline",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "Timeline inconsistency"),
                    suggestion=issue_data.get("suggestion", "Fix timeline"),
                    bible_conflict=True
                ))
        except Exception as e:
            print(f"⚠️  Failed to check timeline: {e}")
        
        return issues
    
    def _check_character_consistency(self, text: str, style_sheet: StyleSheet) -> List[Issue]:
        """Check character consistency"""
        issues = []
        
        for char in style_sheet.characters[:5]:  # Top 5 characters
            prompt = f"""You are a Copy Editor checking CHARACTER CONSISTENCY.

CHARACTER: {char.name}
- Physical: {char.physical_description}
- Age: {char.age}
- Occupation: {char.occupation}

MANUSCRIPT:
{text}

Find contradictions where the manuscript describes {char.name} differently.

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 2, Scene 1",
    "quote": "His blue eyes sparkled",
    "description": "Character inconsistency: {char.name} is described as having 'blue eyes' but Style Sheet says 'brown eyes'",
    "suggestion": "Change to 'brown eyes' to match Style Sheet, or update Style Sheet if this is intentional"
  }}
]

CRITICAL RULES:
1. Quote the CONTRADICTION from the manuscript in "quote"
2. Reference the Style Sheet entry
3. If no errors found, return: []
"""
            
            try:
                response = self.generate(prompt, max_tokens=4000, temperature=0.1)
                char_issues = self.parse_json_response(response)
                
                for issue_data in char_issues:
                    self.issue_counter += 1
                    issues.append(Issue(
                        id=self.issue_counter,
                        stage="copy",
                        severity="major",
                        category="consistency",
                        location=issue_data.get("location", "Unknown"),
                        original_text=issue_data.get("quote", ""),
                        description=f"Character '{char.name}': {issue_data.get('description', 'Inconsistency')}",
                        suggestion=issue_data.get("suggestion", "Fix inconsistency"),
                        bible_conflict=True
                    ))
            except Exception as e:
                print(f"⚠️  Failed to check {char.name}: {e}")
        
        return issues
    
    def _check_house_style(self, text: str, style_sheet: StyleSheet) -> List[Issue]:
        """Check house style compliance"""
        issues = []
        
        rules = style_sheet.custom_rules
        
        prompt = f"""You are a Copy Editor checking HOUSE STYLE compliance.

HOUSE STYLE RULES:
- Oxford comma: {"Required" if rules.oxford_comma else "Not used"}
- Numbers: {rules.number_style}
- Time format: {rules.time_format}
- Quote style: {rules.quote_style} quotes

MANUSCRIPT:
{text}

Find house style violations.

Return JSON array with this EXACT structure:
[
  {{
    "location": "Chapter 1, paragraph 5",
    "quote": "red, white and blue",
    "description": "Oxford comma violation: should have comma before 'and'",
    "suggestion": "Change to: 'red, white, and blue'"
  }}
]

CRITICAL RULES:
1. Quote the ACTUAL VIOLATION in "quote"
2. Show the CORRECTED version
3. If no violations found, return: []
"""
        
        try:
            response = self.generate(prompt, max_tokens=4000, temperature=0.1)
            style_issues = self.parse_json_response(response)
            
            for issue_data in style_issues:
                self.issue_counter += 1
                issues.append(Issue(
                    id=self.issue_counter,
                    stage="copy",
                    severity="minor",
                    category="house_style",
                    location=issue_data.get("location", "Unknown"),
                    original_text=issue_data.get("quote", ""),
                    description=issue_data.get("description", "House style violation"),
                    suggestion=issue_data.get("suggestion", "Apply house style"),
                    bible_conflict=False
                ))
        except Exception as e:
            print(f"⚠️  Failed to check house style: {e}")
        
        return issues
