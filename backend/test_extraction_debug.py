
import asyncio
import os
from dotenv import load_dotenv
from core.llm_client import LLMClient
from agents.style_sheet_extractor import StyleSheetExtractor
from core.style_sheet import StyleSheet

# Load env
load_dotenv()

async def main():
    print("--- Starting Debug Extraction ---")
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key present: {bool(api_key)}")
    if api_key:
        print(f"API Key start: {api_key[:4]}...")
    
    try:
        client = LLMClient()
        print(f"LLM Client initialized. Base URL: {client.base_url}")
        print(f"Model: {client.model}")
        
        extractor = StyleSheetExtractor(client)
        
        # specific short text to test
        text = """
        The old man sat on the bench in Central Park. His name was Arthur, and he was 85 years old. 
        He wore a tattered grey coat. He remembered the day he met Martha at this very spot in 1955.
        She had dropped her red scarf. It was a cold Tuesday in November.
        """
        
        print(f"\nTest Text ({len(text)} chars):\n{text.strip()}\n")
        
        style_sheet = StyleSheet(manuscript_id="debug_test")
        
        print("Running extract_world_building...")
        result = await extractor.extract_world_building(text, style_sheet)
        
        print("\n--- Extraction Results ---")
        print(f"Characters: {len(result.characters)}")
        for c in result.characters:
            print(f" - {c.name} ({c.age})")
            
        print(f"Locations: {len(result.locations)}")
        for l in result.locations:
            print(f" - {l.name}")
            
        print(f"Timeline: {len(result.timeline)}")
        for t in result.timeline:
            print(f" - {t.date}: {t.event}")
            
        print(f"Objects: {len(result.objects)}")
        for o in result.objects:
            print(f" - {o.name}")
            
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
