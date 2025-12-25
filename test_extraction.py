"""
Test Style Sheet Extraction
"""
import sys
sys.path.insert(0, 'backend')

from core.llm_client import LLMClient
from core.style_sheet import StyleSheet
from agents.style_sheet_extractor import StyleSheetExtractor

# Test text
test_text = """
Chapter 1

John Smith walked into the old mill by the river. The abandoned building loomed before him, its ivy-covered walls casting long shadows in the afternoon sun. He clutched the gold locket his mother had given him years ago.

"This place gives me the creeps," muttered Sarah, his partner. She was a tall woman with red hair, always skeptical of John's hunches.

It was Monday, March 15th, and they had exactly three days to solve the case.
"""

print("Testing Style Sheet Extraction...")
print("=" * 50)

# Create LLM client
llm = LLMClient()

# Create empty style sheet
style_sheet = StyleSheet(
    manuscript_id="test-123",
    title="Test Manuscript",
    word_count=len(test_text.split())
)

# Extract entities
extractor = StyleSheetExtractor(llm)
result = extractor.extract(test_text, style_sheet)

print(f"\nCharacters found: {len(result.characters)}")
for char in result.characters:
    print(f"  - {char.name}: {char.physical_description}")

print(f"\nLocations found: {len(result.locations)}")
for loc in result.locations:
    print(f"  - {loc.name}: {loc.description}")

print(f"\nTimeline events: {len(result.timeline)}")
for event in result.timeline:
    print(f"  - {event.date}: {event.event}")

print(f"\nObjects found: {len(result.objects)}")
for obj in result.objects:
    print(f"  - {obj.name}: {obj.description}")

print(f"\nSynopsis: {style_sheet.synopsis[:100]}...")

print("\n" + "=" * 50)
print("Test complete!")
