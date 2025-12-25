"""
Update all agents to use parse_json_response instead of json.loads
"""

import os
import re

# List of agent files to update
agent_files = [
    'backend/agents/consistency_agent.py',
    'backend/agents/developmental_agent.py',
    'backend/agents/prose_quality_agent.py',
    'backend/agents/grammar_agent.py',
    'backend/agents/proofreading_agent.py'
]

for filepath in agent_files:
    print(f"\nUpdating {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace json.loads(response) with self.parse_json_response(response)
    updated_content = re.sub(
        r'json\.loads\(response\)',
        'self.parse_json_response(response)',
        content
    )
    
    # Check if anything changed
    if updated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Updated {filepath}")
    else:
        print(f"⏭️  No changes needed for {filepath}")

print("\n✅ All agents updated!")
