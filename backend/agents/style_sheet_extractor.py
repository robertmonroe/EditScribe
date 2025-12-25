"""
Style Sheet Extractor - Entity Extraction Agent
Analyzes manuscript to extract characters, locations, timeline, and objects
"""

from typing import List, Dict, Any
from core.llm_client import LLMClient
from core.style_sheet import StyleSheet, CharacterStyle, LocationStyle, TimelineEvent, ObjectStyle
import json
import re
import asyncio


class StyleSheetExtractor:
    """
    Extracts entities from manuscript to populate Style Sheet.
    
    Uses LLM to identify:
    - Characters (names, descriptions, traits)
    - Locations (settings, descriptions)
    - Timeline events (dates, sequences)
    - Objects (significant items)
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to ensure valid JSON"""
        # Remove markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
            
        return response.strip()

    async def extract_world_building(self, manuscript_text: str, style_sheet: StyleSheet, on_progress=None) -> StyleSheet:
        """Extract only world-building entities (Characters, Locations, Timeline, Objects)"""
        print("Style Sheet Extractor: Analyzing World Building...")
        
        if on_progress:
            await on_progress("Starting world building analysis...", 0)

        async def extract_chars():
            res = await self._extract_characters(manuscript_text)
            if on_progress: await on_progress("Characters extracted", 25)
            return res

        async def extract_locs():
            res = await self._extract_locations(manuscript_text)
            if on_progress: await on_progress("Locations extracted", 50)
            return res

        async def extract_time():
            res = await self._extract_timeline(manuscript_text)
            if on_progress: await on_progress("Timeline events extracted", 75)
            return res

        async def extract_objs():
            res = await self._extract_objects(manuscript_text)
            if on_progress: await on_progress("Objects extracted", 100)
            return res

        # Run sequentially to respect Free Tier rate limits (15 RPM)
        # and prevent "Stuck at 5%" hang
        
        # 1. Characters
        style_sheet.characters = await extract_chars()
        
        # 2. Locations
        style_sheet.locations = await extract_locs()
        
        # 3. Timeline
        style_sheet.timeline = await extract_time()
        
        # 4. Objects
        style_sheet.objects = await extract_objs()
        
        return style_sheet

    async def generate_synopsis(self, manuscript_text: str, style_sheet: StyleSheet) -> StyleSheet:
        """Generate only the synopsis"""
        print("Style Sheet Extractor: Generating Synopsis...")
        style_sheet.synopsis = await self._extract_synopsis(manuscript_text)
        return style_sheet

    async def extract(self, manuscript_text: str, style_sheet: StyleSheet, on_progress=None) -> StyleSheet:
        """Legacy method: Extract everything"""
        # For backward compatibility, run both
        await self.extract_world_building(manuscript_text, style_sheet, on_progress)
        await self.generate_synopsis(manuscript_text, style_sheet)
        return style_sheet

    async def _extract_synopsis(self, text: str) -> str:
        """Generate a comprehensive professional synopsis from the full manuscript"""
        # Professional Standard: Process the ENTIRE manuscript
        # We rely on the model's large context window (Gemini 1.5 Flash/Pro)
        
        prompt = f"""You are a professional developmental editor creating a master Story Bible.

Read this ENTIRE manuscript and write a comprehensive, professional synopsis (500-1000 words).

REQUIREMENTS:
1. Cover the entire narrative arc from Inciting Incident to Resolution.
2. REVEAL THE ENDING. Do not write a "teaser" or back-cover blurb. This is an internal document for editors.
3. Detail the major plot points, twists, and character turning points.
4. Be objective and clear.

MANUSCRIPT:
{text}

PROFESSIONAL SYNOPSIS:
"""
        try:
            # Use async generation with high token limit
            response = await self.llm.agenerate_content(prompt, max_tokens=4000)
            return response.strip()
        except Exception as e:
            print(f"   Synopsis generation failed: {e}")
            return ""
    
    def _clean_character_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean character data to match Pydantic model"""
        # Clean age
        if "age" in data:
            if isinstance(data["age"], str):
                try:
                    # Extract first number found
                    match = re.search(r'\d+', data["age"])
                    if match:
                        data["age"] = int(match.group())
                    else:
                        data["age"] = None
                except:
                    data["age"] = None
            elif isinstance(data["age"], (float, int)):
                data["age"] = int(data["age"])
            else:
                data["age"] = None
        
        # Clean personality_traits
        if "personality_traits" in data:
            if isinstance(data["personality_traits"], str):
                # Split by comma if it's a string
                data["personality_traits"] = [t.strip() for t in data["personality_traits"].split(",")]
            elif not isinstance(data["personality_traits"], list):
                data["personality_traits"] = []
        else:
            data["personality_traits"] = []
            
        # Ensure other fields are strings
        for field in ["name", "physical_description", "occupation", "speech_patterns", "arc_notes"]:
            if field in data and not isinstance(data[field], str):
                data[field] = str(data[field])
            elif field not in data:
                data[field] = ""
                
        return data

    async def _extract_characters(self, text: str) -> List[CharacterStyle]:
        """Extract character information from FULL manuscript"""
        
        # Professional Standard: Process ENTIRE manuscript
        prompt = f"""You are a professional book editor creating a style sheet.
Analyze this ENTIRE manuscript and extract ALL characters mentioned.

For each character, provide:
- name (full name or how they're referred to)
- age (integer if mentioned, otherwise null)
- physical_description (appearance details)
- occupation (job/role)
- personality_traits (list of strings)
- speech_patterns (how they talk, dialect, catchphrases)
- arc_notes (brief character development notes)

MANUSCRIPT:
{text}

RESPONSE FORMAT:
Return ONLY a raw JSON array. Do not use markdown formatting.
[
  {{
    "name": "John Smith",
    "age": 35,
    "physical_description": "Tall, dark hair",
    "occupation": "Detective",
    "personality_traits": ["determined", "cynical"],
    "speech_patterns": "Short sentences",
    "arc_notes": "Learns to trust"
  }}
]
"""
        
        try:
            response = await self.llm.agenerate_content(prompt, max_tokens=4000)
            cleaned_response = self._clean_json_response(response)
            characters_data = json.loads(cleaned_response)
            
            characters = []
            for char_data in characters_data:
                try:
                    cleaned_data = self._clean_character_data(char_data)
                    characters.append(CharacterStyle(**cleaned_data))
                except Exception as e:
                    print(f"   Skipping invalid character data: {e}")
            
            return characters
        except Exception as e:
            print(f"   Character extraction failed: {e}")
            print(f"   RAW RESPONSE: {response if 'response' in locals() else 'None'}")
            return []
    
    async def _extract_locations(self, text: str) -> List[LocationStyle]:
        """Extract location information from FULL manuscript"""
        
        prompt = f"""You are a professional book editor creating a style sheet.
Analyze this ENTIRE manuscript and extract ALL locations/settings mentioned.

For each location, provide:
- name (location name)
- description (physical description)
- atmosphere (mood, feeling of the place)
- key_features (list of strings)

MANUSCRIPT:
{text}

RESPONSE FORMAT:
Return ONLY a raw JSON array. Do not use markdown formatting.
[
  {{
    "name": "The Old Mill",
    "description": "Abandoned stone mill",
    "atmosphere": "Eerie",
    "key_features": ["waterwheel", "broken windows"]
  }}
]
"""
        
        try:
            response = await self.llm.agenerate_content(prompt, max_tokens=4000)
            cleaned_response = self._clean_json_response(response)
            locations_data = json.loads(cleaned_response)
            
            locations = []
            for loc_data in locations_data:
                # Ensure key_features is a list
                if "key_features" in loc_data and isinstance(loc_data["key_features"], str):
                    loc_data["key_features"] = [f.strip() for f in loc_data["key_features"].split(",")]
                locations.append(LocationStyle(**loc_data))
            
            return locations
        except Exception as e:
            print(f"   Location extraction failed: {e}")
            print(f"   RAW RESPONSE: {response if 'response' in locals() else 'None'}")
            return []
    
    async def _extract_timeline(self, text: str) -> List[TimelineEvent]:
        """Extract timeline events from FULL manuscript"""
        
        prompt = f"""You are a professional book editor creating a style sheet.
Analyze this ENTIRE manuscript and extract timeline events (dates, sequences, time references).
For SHORT STORIES or texts without explicit dates, capture relative time markers (e.g., "The next morning", "After the argument").

For each event, provide:
- date (specific date OR relative time like "Day 1", "The next morning")
- day_of_week (string or null)
- event (what happens)
- chapter_reference (e.g. "Chapter 1")

MANUSCRIPT:
{text}

RESPONSE FORMAT:
Return ONLY a raw JSON array. Do not use markdown formatting.
[
  {{
    "date": "Monday, March 15",
    "day_of_week": "Monday",
    "event": "John arrives in town",
    "chapter_reference": "Chapter 1"
  }}
]
"""
        
        try:
            response = await self.llm.agenerate_content(prompt, max_tokens=4000)
            cleaned_response = self._clean_json_response(response)
            timeline_data = json.loads(cleaned_response)
            
            timeline = []
            for event_data in timeline_data:
                timeline.append(TimelineEvent(**event_data))
            
            return timeline
        except Exception as e:
            print(f"   Timeline extraction failed: {e}")
            print(f"   RAW RESPONSE: {response if 'response' in locals() else 'None'}")
            return []
    
    async def _extract_objects(self, text: str) -> List[ObjectStyle]:
        """Extract significant objects from FULL manuscript"""
        
        prompt = f"""You are a professional book editor creating a style sheet.
Analyze this ENTIRE manuscript and extract SIGNIFICANT objects (items that matter to the plot).

For each object, provide:
- name (object name)
- description (what it looks like)
- color (string or null)
- significance (why it matters)

MANUSCRIPT:
{text}

RESPONSE FORMAT:
Return ONLY a raw JSON array. Do not use markdown formatting.
[
  {{
    "name": "The Locket",
    "description": "Gold heart-shaped locket",
    "color": "gold",
    "significance": "Contains photo of mother"
  }}
]
"""
        
        try:
            response = await self.llm.agenerate_content(prompt, max_tokens=4000)
            cleaned_response = self._clean_json_response(response)
            objects_data = json.loads(cleaned_response)
            
            objects = []
            for obj_data in objects_data:
                objects.append(ObjectStyle(**obj_data))
            
            return objects
        except Exception as e:
            print(f"   Object extraction failed: {e}")
            print(f"   RAW RESPONSE: {response if 'response' in locals() else 'None'}")
            return []
