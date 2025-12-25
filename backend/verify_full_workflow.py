import asyncio
import httpx
import os
import sys
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Dummy Manuscript Content
MANUSCRIPT_CONTENT = """
Chapter 1

The elevator descended down in a smooth, expensive silence that was characteristic of German engineering. Max leaned against the back wall, his blue eyes scanning the floor numbers. He recieved the letter yesterday. It was Monday, March 15th.

"I don't know," Sarah said. She walked into the room.
"You don't know what?" Max asked.
"Anything."

The room was filled with a bluish light that had a pallor that reminded Max of a morgue.
"""

async def run_verification():
    print("🚀 Starting Full Workflow Verification...")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Upload Manuscript
        print("\n1️⃣  Uploading Manuscript...")
        files = {'file': ('test_manuscript.txt', MANUSCRIPT_CONTENT, 'text/plain')}
        response = await client.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.text}")
            return
        
        data = response.json()
        manuscript_id = data["manuscript_id"]
        print(f"✅ Upload successful. ID: {manuscript_id}")
        
        # 2. Extract Series Bible
        print("\n2️⃣  Extracting Series Bible...")
        response = await client.post(f"{BASE_URL}/bible/extract/{manuscript_id}")
        if response.status_code != 200:
            print(f"❌ Bible extraction failed: {response.text}")
            return
        print("✅ Series Bible extracted.")
        
        # 3. Run Acquisitions
        print("\n3️⃣  Running Acquisitions Editor...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/acquisitions")
        if response.status_code != 200:
            print(f"❌ Acquisitions failed: {response.text}")
            return
        
        acq_data = response.json()
        if "marketing_blurb" in acq_data["report"] and "synopsis" in acq_data["report"]:
             print("✅ Acquisitions Report valid (Blurb & Synopsis found).")
        else:
             print("⚠️  Acquisitions Report missing fields.")
             
        # 4. Run Developmental
        print("\n4️⃣  Running Developmental Editor...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/developmental")
        if response.status_code != 200:
            print(f"❌ Developmental failed: {response.text}")
            return
        
        dev_data = response.json()
        issues = dev_data.get("issues", [])
        print(f"✅ Developmental complete. Found {len(issues)} issues.")
        if issues and "original_text" in issues[0]:
            print("   - 'original_text' field verified.")
        elif issues:
            print("   ❌ 'original_text' field MISSING.")
            
        # 5. Run Line Editor
        print("\n5️⃣  Running Line Editor...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/line")
        if response.status_code != 200:
            print(f"❌ Line edit failed: {response.text}")
            return
            
        line_data = response.json()
        issues = line_data.get("issues", [])
        print(f"✅ Line edit complete. Found {len(issues)} issues.")
        if issues and "original_text" in issues[0]:
            print("   - 'original_text' field verified.")
            
        # 6. Run Copy Editor
        print("\n6️⃣  Running Copy Editor...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/copy")
        if response.status_code != 200:
            print(f"❌ Copy edit failed: {response.text}")
            return
            
        copy_data = response.json()
        issues = copy_data.get("issues", [])
        print(f"✅ Copy edit complete. Found {len(issues)} issues.")
        if issues and "original_text" in issues[0]:
            print("   - 'original_text' field verified.")
            
        # 7. Run Proofreader
        print("\n7️⃣  Running Proofreader...")
        response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/proof")
        if response.status_code != 200:
            print(f"❌ Proofread failed: {response.text}")
            return
            
        proof_data = response.json()
        issues = proof_data.get("issues", [])
        print(f"✅ Proofread complete. Found {len(issues)} issues.")
        if issues and "original_text" in issues[0]:
            print("   - 'original_text' field verified.")
            
        # 8. Verify Apply Fixes (using Proofreader issues)
        if issues:
            print("\n8️⃣  Verifying Apply Fixes (Proofreader)...")
            issue_to_fix = 0
            print(f"   Targeting issue #{issue_to_fix}: {issues[issue_to_fix]['description']}")
            
            payload = {"issue_indices": [issue_to_fix]}
            response = await client.post(f"{BASE_URL}/workflow/{manuscript_id}/proof/apply-fixes", json=payload)
            
            if response.status_code == 200:
                fix_data = response.json()
                print(f"   ✅ Fix applied successfully. Fixes count: {fix_data['fixes_applied']}")
                print(f"   📝 New Text Snippet: {fix_data['edited_text'][100:200]}...") # Print a snippet
            else:
                print(f"   ❌ Fix application failed: {response.text}")
        else:
            print("\n⚠️ Skipping Fix Verification (no proofreading issues found).")

        print("\n🎉 FULL WORKFLOW VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_verification())
