"""Main bid generator agent."""
from typing import Optional, Dict
from pydantic import BaseModel

from .analyzer import ProjectAnalyzer, ProjectAnalysis
from .optimizer import BidOptimizer
from ..core.memory import bid_memory


class GeneratedBid(BaseModel):
    """Generated bid with metadata."""
    bid_text: str
    project_analysis: ProjectAnalysis
    word_count: int
    confidence_score: float  # 0-100


class BidGenerator:
    """Main bid generation agent."""
    
    def __init__(self, llm_client, config):
        """Initialize bid generator."""
        self.llm = llm_client
        self.config = config
        self.analyzer = ProjectAnalyzer(llm_client, config.get_skills_list())
        self.optimizer = BidOptimizer(llm_client)
    
    def generate(
        self,
        project_description: str,
        project_name: str = "",
        bid_rank: Optional[int] = None,
        total_bids: Optional[int] = None,
        your_bid_amount: Optional[str] = None
    ) -> GeneratedBid:
        """Generate a bid for the project."""
        
        # Step 1: Analyze project
        analysis = self.analyzer.analyze(project_description, project_name)
        
        # Step 2: Get learning context from past bids
        learning_context = bid_memory.get_context_for_generation()
        
        # Step 3: Generate bid with enhanced system prompt
        system_prompt = f"""You are an EXPERT freelance bid writer who writes WINNING proposals that get hired.

Your mission: Write a BID SO COMPELLING that the client immediately wants to hire you.

═══════════════════════════════════════════════════════════
WINNING BID STRUCTURE (FOLLOW THIS EXACTLY):
═══════════════════════════════════════════════════════════

**OPENING** (1-2 sentences):
Start with "Hi! I can [verb] your [specific deliverable]..." 
Be CONCRETE: "I can build your Python web application" NOT "I can help with your project"
Show you understand EXACTLY what they need.

**EXPERTISE BULLETS** (3 bullet points with * bullets):
Each bullet MUST include:
• A SPECIFIC skill/technology they mentioned
• How you've used it (frameworks, tools, methods)
• A quantifiable achievement or result when possible

Example format:
*   I specialize in [Technology] using [Framework/Tools], having delivered [X number] of similar projects with [specific result/outcome].
*   My expertise in [Required Skill] encompasses [specific techniques/methods], achieving [measurable result like X% performance gain, Y hours saved, etc.].
*   Recent work: [Brief example with concrete metrics], demonstrating [how it's relevant to their need].

**YOUR APPROACH WITH PRICING** (3-4 sentences):
Start with "I will [action verb]..." 
• Describe your SPECIFIC implementation plan
• Break down the key phases/deliverables
• **ALWAYS state a clear price or hourly rate** - e.g., "For this medium-complexity project, I propose $X fixed price" or "My rate is $X/hour"
• Justify your pricing with value: "This includes [list key deliverables], ensuring [specific benefit]"

**TIMELINE & CALL TO ACTION** (2 sentences):
"I can start immediately and deliver within [X days/weeks]."
"Let's discuss your specific requirements and timeline. Ready to get started?"

═══════════════════════════════════════════════════════════
CRITICAL SUCCESS RULES (MUST FOLLOW):
═══════════════════════════════════════════════════════════

✓ ALWAYS include a clear price/rate - THIS IS NON-NEGOTIABLE
✓ ALWAYS quantify your experience with numbers when possible
✓ ALWAYS use bullet format with * (asterisk) for expertise section
✓ ALWAYS mention SPECIFIC frameworks/tools from their requirements
✓ ALWAYS provide a timeline for delivery
✓ Keep 180-280 words total - comprehensive yet scannable
✓ Show confidence: "I will deliver" not "I can try to help"
✓ Tailor opening to directly solve their MAIN problem

✗ NEVER skip the pricing - clients expect it!
✗ NEVER be generic: "I have experience" → "I've completed 15+ Flask applications"
✗ NEVER write long paragraphs - use bullets and short sentences
✗ NEVER say "I read your requirements" (obvious filler)
✗ NEVER list all your skills - only the most relevant 3-4
✗ NEVER give vague timelines like "ASAP" - be specific

═══════════════════════════════════════════════════════════
PRICING GUIDANCE:
═══════════════════════════════════════════════════════════

For Small Projects (<1 week): $200-800 or $25-50/hour
For Medium Projects (1-2 weeks): $800-2500 or $40-75/hour  
For Large Projects (>2 weeks): $2500+ or $60-100/hour

**Always state your price clearly:** Research similar projects, consider complexity, and be competitive but fair.

═══════════════════════════════════════════════════════════
YOUR PROFILE:
═══════════════════════════════════════════════════════════
- Name: {self.config.your_name}
- GitHub: {self.config.your_github}
- Your Skills: {', '.join(self.config.get_skills_list())}

Portfolio Reference Format (use when highly relevant):
When mentioning examples, you can reference: `{self.config.your_github}` or describe similar work with metrics.
{learning_context}

═══════════════════════════════════════════════════════════
EXAMPLE OF PERFECT BID:
═══════════════════════════════════════════════════════════

Hi! I can build your Python web application that serves dynamic pages while automatically processing numeric data in real-time, ensuring seamless delivery of results to your users.

My expertise aligns perfectly with your needs:

*   I specialize in Python web development with Flask and FastAPI, having delivered 20+ production applications with clean routing, templating, and lightweight APIs.
*   My numeric data processing experience includes building statistical calculation engines that handle array manipulations and complex operations with 99.9% accuracy and sub-second response times.
*   Recent project: Built a real-time data dashboard for a client processing 10K+ calculations/minute, demonstrating the exact integration you need between web UI and backend processing.

I will set up a Flask application with modular architecture for scalability. The numeric processing module will efficiently handle your calculations and stream results to the frontend in real-time. Key deliverables include: clean routing structure, optimized calculation routines, responsive web pages, and comprehensive testing. **For this medium-complexity project, I propose $1,200 fixed price**, which includes all development, testing, and deployment support.

I can start immediately and deliver within 7-10 days. Let's discuss your specific data requirements and calculation logic. Ready to get started?

═══════════════════════════════════════════════════════════

Now write a bid following this EXACT structure, ensuring you INCLUDE PRICING."""

        competition_context = ""
        if bid_rank and total_bids:
            competition_context = f"\n\nNote: This is bid #{bid_rank} of {total_bids}. "
            if bid_rank > total_bids * 0.5:
                competition_context += "You're competing with many bids - be concise and highlight unique value."
            else:
                competition_context += "Early bid advantage - be clear and professional."

        sample_work_note = ""
        if self.config.include_samples:
            sample_work_note = "\n\nIMPORTANT: Include a relevant sample work link or demo if applicable to this project type."

        user_prompt = f"""Generate a professional bid for this project:

Project Name: {project_name if project_name else 'Not specified'}

Project Description:
{project_description}

Project Analysis:
- Type: {analysis.project_type}
- Required Skills: {', '.join(analysis.required_skills)}
- Your Matched Skills: {', '.join(analysis.matched_skills)} ({analysis.skill_match_score}% match)
- Key Requirements: {', '.join(analysis.key_requirements)}
- Deliverables: {', '.join(analysis.deliverables)}
{competition_context}
{sample_work_note}

Write the bid text ONLY. No introductions like "Here's the bid:" - just the bid content itself."""

        bid_text = self.llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.7)
        
        # Clean up bid text
        bid_text = bid_text.strip()
        
        # Save to memory for learning
        bid_memory.add_bid(
            project_name=project_name,
            project_description=project_description,
            generated_bid=bid_text,
            total_bids=total_bids,
            budget_range=None,  # Can be added later
            won=None  # Will be updated when result is known
        )
        
        # Calculate confidence based on skill match and bid quality
        word_count = len(bid_text.split())
        confidence = analysis.skill_match_score
        
        # Adjust confidence based on bid length (optimal: 100-250 words)
        if 100 <= word_count <= 250:
            confidence = min(100, confidence + 10)
        elif word_count < 50:
            confidence = max(0, confidence - 20)
        elif word_count > 400:
            confidence = max(0, confidence - 15)
        
        return GeneratedBid(
            bid_text=bid_text,
            project_analysis=analysis,
            word_count=word_count,
            confidence_score=round(confidence, 1)
        )
