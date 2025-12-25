"""
Style Sheet Model - Professional publishing style guide
Replaces Series Bible with industry-standard style sheet
"""

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class CharacterStyle(BaseModel):
    """Character consistency rules"""
    name: str
    age: Optional[int] = None
    physical_description: str = ""
    occupation: str = ""
    personality_traits: List[str] = []
    speech_patterns: str = ""  # How they talk
    arc_notes: str = ""  # Character development notes


class LocationStyle(BaseModel):
    """Location consistency rules"""
    name: str
    description: str
    atmosphere: str = ""
    key_features: List[str] = []


class TimelineEvent(BaseModel):
    """Timeline consistency"""
    date: str
    day_of_week: Optional[str] = None
    event: str
    chapter_reference: str = ""


class ObjectStyle(BaseModel):
    """Object consistency rules"""
    name: str
    description: str
    color: Optional[str] = None
    significance: str = ""


class HouseStyleRules(BaseModel):
    """Chicago Manual of Style + custom rules"""
    
    # Spelling preferences
    spelling_preferences: Dict[str, str] = {}  # "blonde" vs "blond"
    
    # Capitalization
    capitalization_rules: Dict[str, str] = {}  # "Internet" vs "internet"
    
    # Numbers
    number_style: str = "spell_out_under_100"  # or "always_numerals"
    
    # Punctuation
    oxford_comma: bool = True
    em_dash_style: str = "no_spaces"  # "—" vs " — "
    
    # Quotation marks
    quote_style: str = "double"  # "double" or "single"
    
    # Time format
    time_format: str = "12_hour"  # "3:00 p.m." vs "15:00"
    
    # Date format
    date_format: str = "month_day_year"  # "March 15, 2024"


class StyleSheet(BaseModel):
    """
    Professional Style Sheet for manuscript editing.
    
    This is the "Bible" that Copy Editors use to ensure consistency.
    Replaces the Series Bible with industry-standard structure.
    """
    
    # Metadata
    manuscript_id: str
    title: str = ""
    author: str = ""
    genre: str = ""
    target_audience: str = ""
    word_count: int = 0
    synopsis: str = ""  # Brief summary of the story
    
    # House style
    house_style_guide: str = "Chicago Manual of Style, 17th Edition"
    custom_rules: HouseStyleRules = HouseStyleRules()
    
    # Character consistency
    characters: List[CharacterStyle] = []
    
    # World-building consistency
    locations: List[LocationStyle] = []
    objects: List[ObjectStyle] = []
    
    # Timeline consistency
    timeline: List[TimelineEvent] = []
    
    # Terminology
    preferred_terms: Dict[str, str] = {}  # "email" vs "e-mail"
    
    # Notes
    editor_notes: str = ""
    
    # Timestamps
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: dict) -> "StyleSheet":
        """Create from dictionary"""
        return cls(**data)
    
    def update_character(self, name: str, **kwargs):
        """Update character style rules"""
        for char in self.characters:
            if char.name == name:
                for key, value in kwargs.items():
                    setattr(char, key, value)
                self.updated_at = datetime.now()
                return
        
        # Add new character if not found
        self.characters.append(CharacterStyle(name=name, **kwargs))
        self.updated_at = datetime.now()
    
    def add_timeline_event(self, date: str, event: str, **kwargs):
        """Add timeline event"""
        self.timeline.append(TimelineEvent(
            date=date,
            event=event,
            **kwargs
        ))
        self.updated_at = datetime.now()
    
    def get_character(self, name: str) -> Optional[CharacterStyle]:
        """Get character by name"""
        for char in self.characters:
            if char.name.lower() == name.lower():
                return char
        return None
