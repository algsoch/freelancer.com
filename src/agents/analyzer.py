"""Project description analyzer."""
from typing import Dict, List
from pydantic import BaseModel


class ProjectAnalysis(BaseModel):
    """Project analysis result."""
    project_type: str
    required_skills: List[str]
    key_requirements: List[str]
    estimated_complexity: str  # low, medium, high
    estimated_budget_range: str
    deliverables: List[str]
    special_notes: List[str]
    matched_skills: List[str]
    skill_match_score: float  # 0-100


class ProjectAnalyzer:
    """Analyzes project descriptions to extract key information."""
    
    def __init__(self, llm_client, user_skills: List[str]):
        """Initialize analyzer."""
        self.llm = llm_client
        self.user_skills = user_skills
    
    def analyze(self, project_description: str, project_name: str = "") -> ProjectAnalysis:
        """Analyze project description and extract key information."""
        
        # Handle empty or missing descriptions
        if not project_description or project_description.strip() == "" or "No project description found" in project_description:
            return ProjectAnalysis(
                project_type="Unknown Project Type",
                required_skills=[],
                key_requirements=["Project description not available"],
                estimated_complexity="medium",
                estimated_budget_range="Not specified",
                deliverables=["Not specified"],
                special_notes=["Unable to analyze - missing project description"],
                matched_skills=[],
                skill_match_score=0.0
            )
        
        system_prompt = """You are an expert freelance project analyzer. Extract key information from project descriptions.
        
Your task is to analyze the project and return structured information in JSON format with these fields:
- project_type: Type of project (e.g., "Web Scraping", "Web Development", "Data Entry", "Image Processing")
- required_skills: List of required technical skills
- key_requirements: Main requirements from the client
- estimated_complexity: "low", "medium", or "high"
- estimated_budget_range: Estimated budget (e.g., "$50-150", "₹5000-10000")
- deliverables: What the client expects to receive
- special_notes: Important details like deadlines, tools, or specific constraints

Return ONLY valid JSON, no other text. Ensure all fields are present with appropriate defaults if not found."""

        user_prompt = f"""Project Name: {project_name}

Project Description:
{project_description}

Available Skills: {', '.join(self.user_skills)}

Analyze this project and return the information in JSON format."""

        response = self.llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Parse JSON response
        import json
        try:
            # Clean response if needed
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            # Calculate skill match
            required_skills_lower = [s.lower() for s in data.get("required_skills", [])]
            user_skills_lower = [s.lower() for s in self.user_skills]
            
            matched = [skill for skill in data.get("required_skills", []) 
                      if skill.lower() in user_skills_lower]
            
            match_score = (len(matched) / len(required_skills_lower) * 100) if required_skills_lower else 0
            
            return ProjectAnalysis(
                project_type=data.get("project_type", "General"),
                required_skills=data.get("required_skills", []),
                key_requirements=data.get("key_requirements", []),
                estimated_complexity=data.get("estimated_complexity", "medium"),
                estimated_budget_range=data.get("estimated_budget_range", "Not specified"),
                deliverables=data.get("deliverables", []),
                special_notes=data.get("special_notes", []),
                matched_skills=matched,
                skill_match_score=round(match_score, 1)
            )
        except json.JSONDecodeError as e:
            # Fallback to basic analysis
            return ProjectAnalysis(
                project_type="General",
                required_skills=[],
                key_requirements=[],
                estimated_complexity="medium",
                estimated_budget_range="Not specified",
                deliverables=[],
                special_notes=[],
                matched_skills=[],
                skill_match_score=0.0
            )
