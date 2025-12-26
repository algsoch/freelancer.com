"""FastAPI backend for AI Bid Writer."""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.core.llm_client import get_llm_client
from src.core.config import config
from src.core.memory import bid_memory
from src.agents.bid_generator import BidGenerator
from src.agents.optimizer import BidOptimizer
from src.utils.parser import ProjectParser, ParsedProject

app = FastAPI(title="AI Bid Writer", version="1.0.0")

# CORS middleware for React frontend (supports Render + Vercel deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployed environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client and bid generator
try:
    llm_client = get_llm_client()
    bid_generator = BidGenerator(llm_client, config)
    bid_optimizer = BidOptimizer(llm_client)
except Exception as e:
    print(f"Warning: Could not initialize LLM client: {e}")
    llm_client = None
    bid_generator = None
    bid_optimizer = None


class BidRequest(BaseModel):
    """Request model for bid generation."""
    project_name: str
    project_description: str
    bid_rank: Optional[int] = None
    total_bids: Optional[int] = None
    your_bid_amount: Optional[str] = None
    winning_bid_amount: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None


class SmartBidRequest(BaseModel):
    """Request model for smart bid generation with auto-parsing."""
    raw_content: str  # The entire pasted content


class BidResponse(BaseModel):
    """Response model for generated bid."""
    bid_text: str
    project_analysis: dict
    word_count: int
    confidence_score: float
    optimization: Optional[dict] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Bid Writer API",
        "version": "1.0.0",
        "status": "running",
        "llm_configured": llm_client is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": llm_client is not None,
        "ai_provider": config.ai_provider
    }


@app.get("/config")
async def get_config():
    """Get current configuration (without API keys)."""
    return {
        "your_name": config.your_name,
        "your_github": config.your_github,
        "your_skills": config.get_skills_list(),
        "ai_provider": config.ai_provider,
        "default_turnaround": config.default_turnaround,
        "available_providers": ["gemini", "openai", "anthropic"],
        "available_models": {
            "gemini": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"],
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]
        }
    }


@app.post("/generate-bid", response_model=BidResponse)
async def generate_bid(request: BidRequest):
    """Generate a bid for the given project."""
    if not bid_generator:
        raise HTTPException(
            status_code=500,
            detail="LLM client not configured. Please set up your API keys in .env file."
        )
    
    try:
        # Generate bid
        result = bid_generator.generate(
            project_description=request.project_description,
            project_name=request.project_name,
            bid_rank=request.bid_rank,
            total_bids=request.total_bids,
            your_bid_amount=request.your_bid_amount
        )
        
        # Optimize bid
        optimization = None
        try:
            opt_result = bid_optimizer.optimize(
                generated_bid=result.bid_text,
                bid_rank=request.bid_rank,
                total_bids=request.total_bids,
                your_bid_amount=request.your_bid_amount,
                winning_bid_amount=request.winning_bid_amount,
                project_analysis=result.project_analysis.dict()
            )
            optimization = opt_result.dict()
        except Exception as opt_error:
            print(f"Optimization error: {opt_error}")
        
        return BidResponse(
            bid_text=result.bid_text,
            project_analysis=result.project_analysis.dict(),
            word_count=result.word_count,
            confidence_score=result.confidence_score,
            optimization=optimization
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-project", response_model=dict)
async def parse_project(request: SmartBidRequest):
    """Parse pasted project content and extract all information."""
    try:
        parsed = ProjectParser.parse(request.raw_content)
        return {
            "project_name": parsed.project_name,
            "project_description": parsed.project_description,
            "budget_range": parsed.budget_range,
            "bid_rank": parsed.bid_rank,
            "total_bids": parsed.total_bids,
            "average_bid": parsed.average_bid,
            "time_remaining": parsed.time_remaining,
            "client_location": parsed.client_location,
            "client_rating": parsed.client_rating,
            "required_skills": parsed.required_skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse content: {str(e)}")


@app.post("/smart-generate-bid", response_model=BidResponse)
async def smart_generate_bid(request: SmartBidRequest):
    """Parse content and generate bid in one step."""
    if not bid_generator:
        raise HTTPException(
            status_code=500,
            detail="LLM client not configured. Please set up your API keys in .env file."
        )
    
    try:
        # Step 1: Parse the content
        parsed = ProjectParser.parse(request.raw_content)
        
        # Step 2: Generate bid using parsed data
        result = bid_generator.generate(
            project_description=parsed.project_description,
            project_name=parsed.project_name or "Project",
            bid_rank=parsed.bid_rank,
            total_bids=parsed.total_bids,
            your_bid_amount=parsed.average_bid
        )
        
        # Step 3: Optimize bid
        optimization = None
        try:
            opt_result = bid_optimizer.optimize(
                generated_bid=result.bid_text,
                bid_rank=parsed.bid_rank,
                total_bids=parsed.total_bids,
                your_bid_amount=parsed.average_bid,
                winning_bid_amount=None,
                project_analysis=result.project_analysis.dict()
            )
            optimization = opt_result.dict()
        except Exception as opt_error:
            print(f"Optimization error: {opt_error}")
        
        return BidResponse(
            bid_text=result.bid_text,
            project_analysis=result.project_analysis.dict(),
            word_count=result.word_count,
            confidence_score=result.confidence_score,
            optimization=optimization
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refine-bid")
async def refine_bid(request: dict):
    """Refine an existing bid with specific modifications."""
    if not bid_generator:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    try:
        original_bid = request.get("original_bid", "")
        refinement_type = request.get("refinement_type", "reduce_length")
        custom_instruction = request.get("custom_instruction", "")
        project_description = request.get("project_description", "")
        custom_api_key = request.get("api_key")
        custom_model = request.get("model")
        custom_provider = request.get("provider")
        
        if not original_bid:
            raise HTTPException(status_code=400, detail="Original bid is required")
        
        # Get LLM client with custom settings if provided
        if custom_api_key or custom_model or custom_provider:
            from src.core.llm_client import LLMClient
            temp_config = config
            if custom_provider:
                temp_config.ai_provider = custom_provider
            if custom_model:
                temp_config.gemini_model = custom_model
            llm_client = LLMClient(
                provider=custom_provider or config.ai_provider,
                api_key=custom_api_key or (config.gemini_api_key if (custom_provider or config.ai_provider) == "gemini" else config.openai_api_key),
                model=custom_model
            )
        else:
            llm_client = get_llm_client(config)
        
        # Build refinement prompt based on type
        refinement_prompts = {
            "reduce_length": "Make this bid SHORTER and more concise (max 150 words). Keep the key points but remove fluff. Maintain professional tone.",
            "make_casual": "Rewrite this bid in a MORE CASUAL, friendly tone. Use contractions, simpler language, but stay professional. Keep it conversational.",
            "make_formal": "Rewrite this bid in a MORE FORMAL, business-like tone. Use complete sentences, professional language, avoid contractions.",
            "add_urgency": "Add URGENCY and availability emphasis. Mention you can start immediately, work quickly, and deliver fast results. Keep same length.",
            "emphasize_skills": "EMPHASIZE your technical skills and expertise more. Add specific tools, frameworks, and technologies. Show deep knowledge.",
            "add_examples": "Add MORE CONCRETE EXAMPLES of similar work you've done. Be specific about projects and outcomes.",
            "custom": custom_instruction if custom_instruction else "Improve this bid while maintaining its core message."
        }
        
        refinement_instruction = refinement_prompts.get(refinement_type, refinement_prompts["reduce_length"])
        
        system_prompt = f"""You are an expert bid refinement specialist. Your job is improve freelance bids based on specific instructions.

IMPORTANT RULES:
- Keep the Freelancer.com style (start with 'Hi!', use bullets, end with CTA)
- Maintain accuracy - don't make up skills or experience
- Keep it natural and authentic
- Return ONLY the refined bid text, no explanations

Refinement Task: {refinement_instruction}"""
        
        user_prompt = f"""Original Bid:
{original_bid}

Project Context:
{project_description[:500]}

Refine this bid according to the instructions. Return only the improved bid text."""
        
        refined_bid = llm_client.generate(user_prompt, system_prompt=system_prompt, temperature=0.6)
        refined_bid = refined_bid.strip()
        
        # Clean up if LLM added extra formatting
        if refined_bid.startswith('"'):
            refined_bid = refined_bid[1:]
        if refined_bid.endswith('"'):
            refined_bid = refined_bid[:-1]
        
        return {"refined_bid": refined_bid}
    
    except Exception as e:
        print(f"Error refining bid: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/stats")
async def get_memory_stats():
    """Get bid history statistics."""
    try:
        stats = bid_memory.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/update-result")
async def update_bid_result(project_name: str, won: bool):
    """Update whether a bid was won or lost."""
    try:
        bid_memory.update_bid_result(project_name, won)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
