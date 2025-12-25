"""
Series Bible Manager Agent
Extracts characters, locations, timeline, and objects from manuscripts
Uses Claude Sonnet 4.5 for complex entity extraction
"""

import json
from typing import List
from agents.base import Agent
from core.models import SeriesBible, Character, Location, TimelineEvent, Object
from core.llm_client import LLMClient


class SeriesBibleManager(Agent):
    """
    Extracts and manages the Series Bible for a manuscript.
    
    The Series Bible is the Single Source of Truth for:
    - Characters (names, traits, relationships)
    - Locations (places, descriptions)
    - Timeline (dates, events, chronology)
    - Objects (important items, descriptions)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("series_bible", llm_client)
    
    def execute(self, manuscript_text: str, manuscript_id: str) -> SeriesBible:
        """
        Extract Series Bible from manuscript.
        
        Args:
            manuscript_text: Full manuscript text
            manuscript_id: Unique ID for this manuscript
            
        Returns:
            SeriesBible object with extracted entities
        """
        print(f"📖 Extracting Series Bible from manuscript...")
        
        # Extract each entity type
        characters = self._extract_characters(manuscript_text)
        locations = self._extract_locations(manuscript_text)
        timeline = self._extract_timeline(manuscript_text)
        objects = self._extract_objects(manuscript_text)
        
        # Build Series Bible
        bible = SeriesBible(
            manuscript_id=manuscript_id,
            characters=characters,
            locations=locations,
            timeline=timeline,
            objects=objects
        )
        
        print(f"✅ Extracted: {len(characters)} characters, {len(locations)} locations, "
              f"{len(timeline)} events, {len(objects)} objects")
        
        return bible
    
    def _extract_characters(self, text: str) -> List[Character]:
        """Extract character entities"""
        prompt = f"""Analyze this manuscript and extract ALL characters.

For each character, identify:
- Name (full name if available)
- Age (if mentioned)
- Eye color (if mentioned)
- Hair description (if mentioned)
- Occupation (if mentioned)
- Personality traits (brief description)
- First appearance (which chapter)
- Relationships (to other characters)

Manuscript:
{text[:15000]}  # First 15k chars for context

Return ONLY a JSON array of characters in this exact format:
[
  {{
    "name": "Sarah Martinez",
    "age": 28,
    "eye_color": "Blue",
    "hair": "Brown, shoulder-length",
    "occupation": "Detective",
    "personality_traits": "Determined, empathetic, analytical",
    "first_appears": "Chapter 1",
    "relationships": [{{"type": "partner", "name": "Mike Chen"}}],
    "notes": "Protagonist"
  }}
]

Return ONLY the JSON array, no other text."""

        response = self.generate(prompt, max_tokens=3000, temperature=0.3)
        
        try:
            # Parse JSON
            characters_data = json.loads(response)
            
            # Clean up age field (convert string to int if needed)
            for char in characters_data:
                if 'age' in char and isinstance(char['age'], str):
                    # Extract first number from string like "35 (Chapter 1)"
                    import re
                    age_match = re.search(r'\d+', char['age'])
                    char['age'] = int(age_match.group()) if age_match else None
            
            return [Character(**char) for char in characters_data]
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                characters_data = json.loads(json_match.group())
                # Clean up age field
                for char in characters_data:
                    if 'age' in char and isinstance(char['age'], str):
                        age_match = re.search(r'\d+', char['age'])
                        char['age'] = int(age_match.group()) if age_match else None
                return [Character(**char) for char in characters_data]
            return []
        except Exception as e:
            print(f"Error parsing characters: {e}")
            return []
    
    def _extract_locations(self, text: str) -> List[Location]:
        """Extract location entities"""
        prompt = f"""Analyze this manuscript and extract ALL important locations.

For each location, identify:
- Name
- Type (e.g., "Police Station", "Residence", "City")
- Description (brief)
- First appearance (which chapter)

Manuscript:
{text[:15000]}

Return ONLY a JSON array of locations:
[
  {{
    "name": "Old Harbor Precinct",
    "type": "Police Station",
    "description": "Brick building, 3 floors, downtown",
    "first_appears": "Chapter 1"
  }}
]

Return ONLY the JSON array, no other text."""

        response = self.generate(prompt, max_tokens=2000, temperature=0.3)
        
        try:
            locations_data = json.loads(response)
            return [Location(**loc) for loc in locations_data]
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                locations_data = json.loads(json_match.group())
                return [Location(**loc) for loc in locations_data]
            return []
    
    def _extract_timeline(self, text: str) -> List[TimelineEvent]:
        """Extract timeline events"""
        prompt = f"""Analyze this manuscript and extract the TIMELINE of events.

For each date/event, identify:
- Date (if mentioned, format: YYYY-MM-DD)
- Day of week (if mentioned)
- Events that happened on that day
- Which chapter

Manuscript:
{text[:15000]}

Return ONLY a JSON array of timeline events:
[
  {{
    "date": "2023-10-15",
    "day_of_week": "Monday",
    "events": ["Sarah receives the case", "First crime scene investigation"],
    "chapter": "Chapter 1"
  }}
]

Return ONLY the JSON array, no other text."""

        response = self.generate(prompt, max_tokens=2000, temperature=0.3)
        
        try:
            timeline_data = json.loads(response)
            return [TimelineEvent(**event) for event in timeline_data]
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                timeline_data = json.loads(json_match.group())
                return [TimelineEvent(**event) for event in timeline_data]
            return []
    
    def _extract_objects(self, text: str) -> List[Object]:
        """Extract important objects/items"""
        prompt = f"""Analyze this manuscript and extract IMPORTANT objects or items that are mentioned multiple times or are significant to the plot.

For each object, identify:
- Name
- Description
- Color (if mentioned)
- First appearance (which chapter)

Manuscript:
{text[:15000]}

Return ONLY a JSON array of objects:
[
  {{
    "name": "Sarah's Red Coat",
    "description": "Wool, knee-length",
    "color": "Red",
    "first_appears": "Chapter 1"
  }}
]

Return ONLY the JSON array, no other text."""

        response = self.generate(prompt, max_tokens=1500, temperature=0.3)
        
        try:
            objects_data = json.loads(response)
            return [Object(**obj) for obj in objects_data]
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                objects_data = json.loads(json_match.group())
                return [Object(**obj) for obj in objects_data]
            return []
