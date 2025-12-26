"""Configuration management for AI Bid Writer."""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class AppConfig(BaseModel):
    """Application configuration."""
    
    # AI Provider settings
    ai_provider: str = Field(default="gemini", description="AI provider: gemini, openai, or anthropic")
    
    # Gemini settings
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model (gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro)")
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model")
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model")
    
    # User profile
    your_name: str = Field(default="Vicky Kumar", description="Your name")
    your_github: str = Field(default="https://www.github.com/algsoch", description="Your GitHub URL")
    your_linkedin: str = Field(default="https://www.linkedin.com/in/algsoch", description="Your LinkedIn URL")
    your_resume: str = Field(default="", description="Your resume URL")
    your_skills: str = Field(default="Python,JavaScript,Web Scraping,Data Science", description="Your skills")
    
    # Bid strategy
    default_turnaround: str = Field(default="24-48 hours", description="Default turnaround time")
    include_samples: bool = Field(default=True, description="Include sample work in bids")
    competitive_pricing: bool = Field(default=True, description="Use competitive pricing strategy")
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        return cls(
            ai_provider=os.getenv("AI_PROVIDER", "gemini"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            your_name=os.getenv("YOUR_NAME", "Vicky Kumar"),
            your_github=os.getenv("YOUR_GITHUB", "https://www.github.com/algsoch"),
            your_linkedin=os.getenv("YOUR_LINKEDIN", "https://www.linkedin.com/in/algsoch"),
            your_resume=os.getenv("YOUR_RESUME", ""),
            your_skills=os.getenv("YOUR_SKILLS", "Python,JavaScript,Web Scraping,Data Science"),
            default_turnaround=os.getenv("DEFAULT_TURNAROUND", "24-48 hours"),
            include_samples=os.getenv("INCLUDE_SAMPLES", "true").lower() == "true",
            competitive_pricing=os.getenv("COMPETITIVE_PRICING", "true").lower() == "true",
        )
    
    def get_skills_list(self) -> list[str]:
        """Get skills as a list."""
        return [skill.strip() for skill in self.your_skills.split(",")]


# Global config instance
config = AppConfig.from_env()
