"""
Base Agent class for all EditScribe agents
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.llm_client import LLMClient


class Agent(ABC):
    """Base class for all review and editing agents"""
    
    def __init__(self, agent_name: str, llm_client: LLMClient):
        """
        Initialize agent.
        
        Args:
            agent_name: Name of the agent (used for LLM routing)
            llm_client: LLM client instance
        """
        self.agent_name = agent_name
        self.llm_client = llm_client
        self.context_id = None
        
    def set_context(self, context_id: str):
        """Set execution context ID (e.g. manuscript_id) for cancellation"""
        self.context_id = context_id
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function"""
        pass
    
    def generate(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """
        Generate content using the appropriate LLM for this agent.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        return self.llm_client.generate(
            agent_name=self.agent_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_id=self.context_id
        )
    
    def parse_json_response(self, response: str):
        """
        Parse JSON from LLM response, stripping markdown code fences if present.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON object
        """
        import json
        import re
        
        # Strip markdown code fences if present
        # Matches: ```json\n...\n``` or ```\n...\n```
        response = response.strip()
        if response.startswith('```'):
            # Remove opening fence
            response = re.sub(r'^```(?:json)?\s*\n', '', response)
            # Remove closing fence
            response = re.sub(r'\n```\s*$', '', response)
        
        return json.loads(response)
