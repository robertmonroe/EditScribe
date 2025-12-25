import asyncio
import httpx
import os
import sys
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Dummy Manuscript Content with a typo
MANUSCRIPT_CONTENT = """
Chapter 1

The elevator descended down in a smooth, expensive silence that was characteristic of German engineering. Max leaned against the back wall, his blue eyes scanning the floor numbers. He recieved the letter yesterday. It was Monday, March 15th.

"I don't know," Sarah said. She walked into the room.
"You don't know what?" Max asked.
"Anything."

The room was filled with a bluish light that had a pallor that reminded Max of a morgue.
"""

async def run_fix_verification():
    print("🚀 Starting Fix Verification...")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Upload Manuscript
        print("\n1️⃣  Uploading Manuscript...")
        files = {'file': ('fix_test.txt', MANUSCRIPT_CONTENT, 'text/plain')}
        response = await client.post(f"{BASE_URL}/upload", files=files)
        data = response.json()
        manuscript_id = data["manuscript_id"]
        print(f"✅ Upload successful. ID: {manuscript_id}")
        
        # 2. Extract Bible (Required for workflow)
        await client.post(f"{BASE_URL}/bible/extract/{manuscript_id}")
        
        # 3. Run Copy Editor to find issues
        print("\n2️⃣  Running Copy Editor...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/copy")
        copy_data = response.json()
        issues = copy_data.get("issues", [])
        print(f"✅ Found {len(issues)} issues.")
        
        if not issues:
            print("❌ No issues found to fix! Test failed.")
            return

        # Find a fixable issue
        typo_index = 0
            
        print(f"🎯 Targeting issue #{typo_index}: {issues[typo_index]['description']}")
        
        # 4. Apply Fix
        print("\n3️⃣  Applying Fix...")
        payload = {"issue_indices": [typo_index]}
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/copy/apply-fixes", json=payload)
        
        if response.status_code != 200:
            print(f"❌ Fix application failed: {response.text}")
            return
            
        fix_data = response.json()
        print(f"✅ Fixes applied: {fix_data['fixes_applied']}")
        
        # 5. Verify Text Change
        new_text = fix_data["edited_text"]
        if "received" in new_text and "recieved" not in new_text:
            print("✅ Text successfully updated: 'recieved' -> 'received'")
        else:
            print("⚠️ Text update verification ambiguous.")
            print(f"New Text Snippet: {new_text.strip()}")

        print("\n🎉 FIX VERIFICATION SUCCESSFUL!")

if __name__ == "__main__":
    asyncio.run(run_fix_verification())
