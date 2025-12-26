"""LLM client for interacting with OpenAI and Anthropic APIs."""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from .config import config


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text from prompt."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using OpenAI API."""
        messages: List[Dict[str, str]] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        
        return response.choices[0].message.content or ""


class AnthropicClient(LLMClient):
    """Anthropic API client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using Anthropic API."""
        kwargs = {
            "model": self.model,
            "max_tokens": 2000,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        return response.content[0].text


class GeminiClient(LLMClient):
    """Google Gemini API client with automatic fallback."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """Initialize Gemini client."""
        try:
            from google import genai
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-genai")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.api_key = api_key
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using Gemini API with automatic model fallback."""
        # Combine system prompt with user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": 2000,
        }
        
        # Try primary model, fallback to alternatives if quota exceeded
        models_to_try = [self.model_name, "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
        last_error = None
        
        for model_name in models_to_try:
            try:
                config = {
                    "temperature": temperature,
                    "max_output_tokens": 2000,
                }
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=config
                )
                
                return response.text
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                # Check if it's a quota error
                if "quota" in error_str or "429" in error_str:
                    print(f"⚠️  Quota exceeded for {model_name}, trying next model...")
                    continue
                else:
                    # If it's not a quota error, raise immediately
                    raise
        
        # If all models failed, raise the last error with helpful message
        raise Exception(
            f"All Gemini models exhausted. Last error: {last_error}\n"
            f"💡 Solution: Try OpenAI or Anthropic by setting AI_PROVIDER in .env\n"
            f"   Or wait for quota reset: https://ai.dev/usage"
        )


def get_llm_client() -> LLMClient:
    """Get configured LLM client."""
    provider = config.ai_provider.lower()
    
    if provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        return OpenAIClient(api_key=config.openai_api_key, model=config.openai_model)
    
    elif provider == "anthropic":
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env file")
        return AnthropicClient(api_key=config.anthropic_api_key, model=config.anthropic_model)
    
    elif provider == "gemini":
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in .env file")
        return GeminiClient(api_key=config.gemini_api_key, model=config.gemini_model)
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider}. Use 'openai', 'anthropic', or 'gemini'")
