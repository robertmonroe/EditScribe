"""
Data models for Series Bible
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Character entity"""
    name: str
    age: Optional[int] = None
    eye_color: Optional[str] = None
    hair: Optional[str] = None
    occupation: Optional[str] = None
    personality_traits: Optional[str] = None
    first_appears: Optional[str] = None  # e.g., "Chapter 1"
    relationships: List[Dict[str, str]] = Field(default_factory=list)  # [{"type": "partner", "name": "John"}]
    notes: Optional[str] = None


class Location(BaseModel):
    """Location entity"""
    name: str
    type: Optional[str] = None  # e.g., "Police Station", "Residence"
    description: Optional[str] = None
    first_appears: Optional[str] = None
    notes: Optional[str] = None


class TimelineEvent(BaseModel):
    """Timeline event"""
    date: Optional[str] = None  # e.g., "2023-10-15"
    day_of_week: Optional[str] = None  # e.g., "Monday"
    events: List[str] = Field(default_factory=list)
    chapter: Optional[str] = None
    notes: Optional[str] = None


class Object(BaseModel):
    """Important object/item"""
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    first_appears: Optional[str] = None
    notes: Optional[str] = None


class SeriesBible(BaseModel):
    """Complete Series Bible for a manuscript"""
    manuscript_id: str
    title: Optional[str] = None
    genre: Optional[str] = None
    
    characters: List[Character] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    objects: List[Object] = Field(default_factory=list)
    
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "SeriesBible":
        """Create from dictionary"""
        return cls(**data)
