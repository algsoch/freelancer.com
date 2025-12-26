"""Bid optimizer for improving bid quality and competitiveness."""
from typing import Dict, List, Optional
from pydantic import BaseModel


class BidOptimization(BaseModel):
    """Bid optimization suggestions."""
    pricing_advice: str
    positioning_advice: str
    improvements: List[str]
    warnings: List[str]
    estimated_win_probability: float  # 0-100


class BidOptimizer:
    """Optimizes bids based on competition and project details."""
    
    def __init__(self, llm_client):
        """Initialize optimizer."""
        self.llm = llm_client
    
    def optimize(
        self,
        generated_bid: str,
        bid_rank: Optional[int] = None,
        total_bids: Optional[int] = None,
        your_bid_amount: Optional[str] = None,
        winning_bid_amount: Optional[str] = None,
        project_analysis: Optional[Dict] = None
    ) -> BidOptimization:
        """Provide optimization suggestions for a generated bid."""
        
        system_prompt = """You are an expert freelance bid optimizer. Analyze bids and provide actionable improvement suggestions.

Consider:
1. Pricing competitiveness
2. Bid positioning and rank
3. Clarity and professionalism
4. Relevance to project requirements
5. Win probability

Return suggestions in JSON format with:
- pricing_advice: Advice on bid amount
- positioning_advice: How to stand out
- improvements: List of specific improvements
- warnings: Any red flags or concerns
- estimated_win_probability: 0-100 score"""

        competition_info = ""
        if bid_rank and total_bids:
            competition_info = f"\nBid Rank: #{bid_rank} of {total_bids} bids"
        if your_bid_amount:
            competition_info += f"\nYour Bid: {your_bid_amount}"
        if winning_bid_amount:
            competition_info += f"\nWinning Bid: {winning_bid_amount}"
        
        project_info = ""
        if project_analysis:
            project_info = f"\nProject Type: {project_analysis.get('project_type', 'Unknown')}"
            project_info += f"\nComplexity: {project_analysis.get('estimated_complexity', 'medium')}"
            project_info += f"\nSkill Match: {project_analysis.get('skill_match_score', 0)}%"

        user_prompt = f"""Analyze this bid and provide optimization suggestions:

Generated Bid:
{generated_bid}
{competition_info}
{project_info}

Provide optimization suggestions in JSON format."""

        response = self.llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.4)
        
        # Parse JSON response
        import json
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            return BidOptimization(
                pricing_advice=data.get("pricing_advice", "Pricing appears competitive"),
                positioning_advice=data.get("positioning_advice", "Good positioning"),
                improvements=data.get("improvements", []),
                warnings=data.get("warnings", []),
                estimated_win_probability=min(100, max(0, data.get("estimated_win_probability", 50)))
            )
        except json.JSONDecodeError:
            # Fallback optimization with smart defaults
            win_prob = 50.0
            if bid_rank and total_bids:
                # Better rank = higher probability
                win_prob = max(20, 100 - (bid_rank / total_bids * 80))
            
            # Better pricing advice
            pricing_advice = "Research competitor bids - aim for middle range to balance value and competitiveness"
            if your_bid_amount:
                pricing_advice = f"Your bid of {your_bid_amount} looks reasonable for this project"
            
            return BidOptimization(
                pricing_advice=pricing_advice,
                positioning_advice="Emphasize unique skills and quick turnaround to stand out",
                improvements=[
                    "Add a concrete timeline or milestone breakdown",
                    "Include specific technologies you'll use",
                    "Mention 1-2 similar projects you've completed"
                ],
                warnings=[],
                estimated_win_probability=round(win_prob, 1)
            )
