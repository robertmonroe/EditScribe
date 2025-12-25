"""
Issue model for review agents
"""

from pydantic import BaseModel
from typing import Optional


class Issue(BaseModel):
    """Represents an issue found during review"""
    
    id: int
    stage: str  # developmental, line, copy, proof
    severity: str  # critical, major, minor
    category: str  # plot_hole, grammar, consistency, etc
    location: str  # Chapter 3, paragraph 5
    original_text: str = ""  # The text causing the issue
    description: str
    suggestion: str
    bible_conflict: bool = False  # True if conflicts with Series Bible
    status: str = "open"  # open, applied, ignored
    
    def __str__(self):
        conflict_marker = "⚠️ BIBLE CONFLICT: " if self.bible_conflict else ""
        return f"[{self.severity.upper()}] {conflict_marker}{self.description}"
    
    def to_dict(self):
        """Convert Issue to dictionary for API responses"""
        return self.model_dump()
