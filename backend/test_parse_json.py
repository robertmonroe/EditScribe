"""
Test parse_json_response helper
"""

import sys
sys.path.append('.')

from agents.base import Agent
from core.llm_client import LLMClient

class TestAgent(Agent):
    def execute(self):
        pass

# Test the parse_json_response method
llm = LLMClient()
agent = TestAgent("test", llm)

# Test with markdown fence
response_with_fence = """```json
[
  {
    "location": "Test",
    "description": "Test desc",
    "suggestion": "Test sug"
  }
]
```"""

# Test without fence
response_without_fence = """[
  {
    "location": "Test2",
    "description": "Test desc2",
    "suggestion": "Test sug2"
  }
]"""

print("Testing parse_json_response...")
print("\n1. With markdown fence:")
result1 = agent.parse_json_response(response_with_fence)
print(f"✅ Parsed: {result1}")

print("\n2. Without markdown fence:")
result2 = agent.parse_json_response(response_without_fence)
print(f"✅ Parsed: {result2}")

print("\n✅ All tests passed!")
