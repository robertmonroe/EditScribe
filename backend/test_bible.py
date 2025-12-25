"""
Test script for Series Bible Manager
Run this to test the Bible extraction on a sample manuscript
"""

import sys
sys.path.append('.')

from core.llm_client import LLMClient
from agents.series_bible_manager import SeriesBibleManager
import json


# Sample manuscript for testing
SAMPLE_MANUSCRIPT = """
# Chapter 1: The Case

Detective Sarah Martinez pushed through the precinct doors, her red wool coat dripping with rain. At 28, she was the youngest detective at Old Harbor Precinct, but her sharp blue eyes missed nothing.

"Morning, Sarah," called her partner, Detective Mike Chen, a 35-year-old veteran with black hair and a perpetual five o'clock shadow. He held up a manila folder. "We've got a new case."

Sarah hung her coat on the rack and joined Mike at his desk. The precinct was a three-story brick building in downtown Harbor City, built in the 1950s and showing its age.

"What do we have?" Sarah asked, accepting the coffee Mike offered.

"Missing person. Emily Martinez—wait, any relation?"

Sarah's expression tightened. "My sister. When did she go missing?"

"Yesterday. Monday, October 15th, 2023. Last seen at her apartment on Elm Street around 8 PM."

# Chapter 2: The Investigation

The next day, Tuesday, October 16th, Sarah and Mike drove to Emily's apartment. It was a small studio in the arts district, cluttered with paintings and sketches.

"She's an artist," Sarah explained, her voice catching. "Always has been."

Mike examined the apartment carefully. "No signs of struggle. Her blue coat is missing—the one she always wears."

Sarah shook her head. "Emily doesn't have a blue coat. She has a green one, the one I gave her last Christmas."

They interviewed the neighbor, Mrs. Chen (no relation to Mike), an elderly woman who lived next door.

# Chapter 3: The Breakthrough

On Wednesday, October 17th, Sarah received a call that changed everything. Emily had been found safe at a friend's house in the suburbs. She'd simply needed time away to work on her art.

Sarah's relief was palpable as she drove to pick up her sister, her red coat folded neatly in the passenger seat—a reminder of the rainy day this all began.
"""


def main():
    """Test the Series Bible Manager"""
    print("=" * 60)
    print("EditScribe - Series Bible Manager Test")
    print("=" * 60)
    print()
    
    # Initialize LLM client
    print("Initializing LLM client...")
    llm_client = LLMClient()
    
    # Initialize Series Bible Manager
    print("Initializing Series Bible Manager...")
    bible_manager = SeriesBibleManager(llm_client)
    
    # Extract Bible
    print("\nExtracting Series Bible from sample manuscript...")
    print("-" * 60)
    
    bible = bible_manager.execute(
        manuscript_text=SAMPLE_MANUSCRIPT,
        manuscript_id="test_001"
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("SERIES BIBLE RESULTS")
    print("=" * 60)
    
    print(f"\n📚 CHARACTERS ({len(bible.characters)}):")
    print("-" * 60)
    for char in bible.characters:
        print(f"\n{char.name}")
        if char.age:
            print(f"  Age: {char.age}")
        if char.eye_color:
            print(f"  Eyes: {char.eye_color}")
        if char.hair:
            print(f"  Hair: {char.hair}")
        if char.occupation:
            print(f"  Occupation: {char.occupation}")
        if char.personality_traits:
            print(f"  Traits: {char.personality_traits}")
        if char.first_appears:
            print(f"  First appears: {char.first_appears}")
        if char.relationships:
            print(f"  Relationships: {char.relationships}")
    
    print(f"\n\n📍 LOCATIONS ({len(bible.locations)}):")
    print("-" * 60)
    for loc in bible.locations:
        print(f"\n{loc.name}")
        if loc.type:
            print(f"  Type: {loc.type}")
        if loc.description:
            print(f"  Description: {loc.description}")
        if loc.first_appears:
            print(f"  First appears: {loc.first_appears}")
    
    print(f"\n\n📅 TIMELINE ({len(bible.timeline)}):")
    print("-" * 60)
    for event in bible.timeline:
        print(f"\n{event.date} ({event.day_of_week})")
        for e in event.events:
            print(f"  • {e}")
        if event.chapter:
            print(f"  Chapter: {event.chapter}")
    
    print(f"\n\n🎯 OBJECTS ({len(bible.objects)}):")
    print("-" * 60)
    for obj in bible.objects:
        print(f"\n{obj.name}")
        if obj.color:
            print(f"  Color: {obj.color}")
        if obj.description:
            print(f"  Description: {obj.description}")
        if obj.first_appears:
            print(f"  First appears: {obj.first_appears}")
    
    # Save to JSON
    output_file = "test_bible.json"
    with open(output_file, 'w') as f:
        json.dump(bible.to_dict(), f, indent=2)
    
    print(f"\n\n✅ Series Bible saved to: {output_file}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
