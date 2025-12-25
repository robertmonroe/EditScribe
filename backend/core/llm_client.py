"""
LLM Client for EditScribe - Multi-Provider Support
Supports: Google Gemini, Anthropic Claude, OpenRouter
"""

from openai import OpenAI, AsyncOpenAI
import anthropic
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
from dotenv import load_dotenv
import os
from typing import Optional
from enum import Enum

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class LLMClient:
    """Unified LLM client with multi-provider support"""
    
    # Model defaults per provider
    DEFAULT_MODELS = {
        LLMProvider.GEMINI: "gemini-3-flash-preview",
        LLMProvider.ANTHROPIC: "claude-opus-4-5-20251101",
        LLMProvider.OPENROUTER: "anthropic/claude-opus-4.5",
    }
    
    def __init__(self, provider: str = None, model: str = None):
        """Initialize LLM client with specified provider"""
        provider_str = provider or os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        try:
            self.provider = LLMProvider(provider_str.lower())
        except ValueError:
            logger.warning(f"Unknown provider '{provider_str}', defaulting to gemini")
            self.provider = LLMProvider.GEMINI
        
        self.model = model or self.DEFAULT_MODELS[self.provider]
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        
        self._init_client()
        
        logger.info(f"LLM Client initialized: {self.provider.value} → {self.model}")
        print(f"🤖 LLM: {self.provider.value} → {self.model}")
    
    def _init_client(self):
        """Initialize the appropriate client based on provider"""
        if self.provider == LLMProvider.GEMINI:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=300.0
            )
            self.async_client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=300.0
            )
            self._use_anthropic_sdk = False
            
        elif self.provider == LLMProvider.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            self.async_anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
            self._use_anthropic_sdk = True
            
        elif self.provider == LLMProvider.OPENROUTER:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment")
            
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=300.0,
                default_headers={
                    "HTTP-Referer": "https://editscribe.local",
                    "X-Title": "EditScribe"
                }
            )
            self.async_client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=300.0,
                default_headers={
                    "HTTP-Referer": "https://editscribe.local",
                    "X-Title": "EditScribe"
                }
            )
            self._use_anthropic_sdk = False
    
    def switch_provider(self, provider: str, model: str = None):
        """Switch to a different provider"""
        try:
            self.provider = LLMProvider(provider.lower())
        except ValueError:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.model = model or self.DEFAULT_MODELS[self.provider]
        self._init_client()
        logger.info(f"Switched to: {self.provider.value} → {self.model}")
        print(f"🔄 Switched LLM: {self.provider.value} → {self.model}")
    
from core.cancellation import cancellation_manager

class CancelledException(Exception):
    pass

# ... imports ...

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def generate_content(
        self,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        system_prompt: str = None,
        context_id: str = None
    ) -> str:
        """Generate content using configured provider"""
        # Check cancellation
        if context_id and cancellation_manager.is_cancelled(context_id):
            print(f"🛑 Operation cancelled for {context_id}")
            raise CancelledException("Operation cancelled by user")

        try:
            self.total_requests += 1
            
            if self._use_anthropic_sdk:
                # Anthropic SDK
                message = self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt or "You are a professional manuscript editor.",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                # Track tokens (Anthropic returns usage)
                if hasattr(message, 'usage'):
                    self.total_input_tokens += getattr(message.usage, 'input_tokens', 0)
                    self.total_output_tokens += getattr(message.usage, 'output_tokens', 0)
                return message.content[0].text.strip()
            else:
                # OpenAI-compatible (Gemini, OpenRouter)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                # Track tokens (OpenAI-compatible returns usage)
                if hasattr(response, 'usage') and response.usage:
                    self.total_input_tokens += getattr(response.usage, 'prompt_tokens', 0)
                    self.total_output_tokens += getattr(response.usage, 'completion_tokens', 0)
                return response.choices[0].message.content.strip()
        
        except CancelledException:
            raise
        except Exception as e:
            logger.exception(f"LLM API error: {e}")
            print(f"❌ LLM Error: {e}")
            return ""

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def agenerate_content(
        self,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        system_prompt: str = None,
        context_id: str = None
    ) -> str:
        """Async version of generate_content"""
        # Check cancellation
        if context_id and cancellation_manager.is_cancelled(context_id):
            raise CancelledException("Operation cancelled by user")
            
        try:
            if self._use_anthropic_sdk:
                # Anthropic SDK (async)
                message = await self.async_anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt or "You are a professional manuscript editor.",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                return message.content[0].text.strip()
            else:
                # OpenAI-compatible (async)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content.strip()
        
        except CancelledException:
            raise
        except Exception as e:
            logger.exception(f"Async LLM API error: {e}")
            print(f"❌ Async LLM Error: {e}")
            return ""
    
    def generate(
        self,
        agent_name: str,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        context_id: str = None
    ) -> str:
        """Generate content (legacy compatibility method)"""
        return self.generate_content(prompt, max_tokens, temperature, context_id=context_id)
    
    @property
    def current_provider(self) -> str:
        """Get current provider name"""
        return self.provider.value
    
    @property
    def current_model(self) -> str:
        """Get current model name"""
        return self.model
    
    def get_usage_stats(self) -> dict:
        """Get token usage statistics"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_requests": self.total_requests
        }
    
    def reset_usage_stats(self):
        """Reset token counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
