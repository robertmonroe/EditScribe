"""
Quick test to verify LLM is working
"""

import sys
sys.path.append('.')

from core.llm_client import LLMClient

# Test LLM
llm = LLMClient()

prompt = """Return ONLY a JSON array with one test issue:
[
  {
    "location": "Test location",
    "description": "Test description", 
    "suggestion": "Test suggestion"
  }
]
"""

print("Testing LLM...")
response = llm.generate(
    agent_name="consistency",
    prompt=prompt,
    max_tokens=200,
    temperature=0.1
)

print(f"\nLLM Response:")
print(response)
print(f"\nResponse length: {len(response)} chars")
