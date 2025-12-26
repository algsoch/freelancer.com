"""Parser for extracting project details from pasted content."""
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ParsedProject(BaseModel):
    """Parsed project information."""
    project_name: Optional[str] = None
    project_description: str
    budget_range: Optional[str] = None
    bid_rank: Optional[int] = None
    total_bids: Optional[int] = None
    average_bid: Optional[str] = None
    time_remaining: Optional[str] = None
    client_location: Optional[str] = None
    client_rating: Optional[str] = None
    required_skills: Optional[list[str]] = []


class ProjectParser:
    """Parses pasted project content to extract structured information."""
    
    @staticmethod
    def parse(raw_content: str) -> ParsedProject:
        """Parse raw pasted content and extract project details."""
        
        # Extract project name (usually the first line or title)
        project_name = ProjectParser._extract_project_name(raw_content)
        
        # Extract project description (the main requirements text)
        project_description = ProjectParser._extract_description(raw_content)
        
        # Extract budget
        budget_range = ProjectParser._extract_budget(raw_content)
        
        # Extract bid information
        bid_info = ProjectParser._extract_bid_info(raw_content)
        
        # Extract client information
        client_info = ProjectParser._extract_client_info(raw_content)
        
        # Extract required skills
        required_skills = ProjectParser._extract_skills(raw_content)
        
        return ParsedProject(
            project_name=project_name,
            project_description=project_description,
            budget_range=budget_range,
            bid_rank=bid_info.get('rank'),
            total_bids=bid_info.get('total'),
            average_bid=bid_info.get('average'),
            time_remaining=bid_info.get('time_remaining'),
            client_location=client_info.get('location'),
            client_rating=client_info.get('rating'),
            required_skills=required_skills
        )
    
    @staticmethod
    def _extract_project_name(content: str) -> Optional[str]:
        """Extract project title/name."""
        lines = content.strip().split('\n')
        # Usually the first significant line
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('$'):
                # Skip common headers and UI elements
                if line.lower() not in ['open', 'bids', 'details', 'proposals', 'project details', 'average bid']:
                    # Skip lines that are just numbers
                    if not re.match(r'^\d+$', line):
                        return line
        return None
    
    @staticmethod
    def _extract_description(content: str) -> str:
        """Extract ONLY the actual project description, removing ALL UI noise."""
        
        # If content is too short, it's probably not valid
        if not content or len(content.strip()) < 50:
            return "Please paste the complete project description from Freelancer.com including the full project details."
        
        # Remove everything before the actual description starts
        # Look for the first paragraph that starts with "I'm" or "I am" or similar
        description_start_patterns = [
            r"I'm", r"I am", r"We need", r"We are", r"We're", r"Looking for",
            r"Need a", r"Need an", r"Seeking", r"Required:", r"Project:",
            r"This project", r"The project", r"My project"
        ]
        
        lines = content.split('\n')
        description_started = False
        description_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if description_started:
                    description_lines.append('')  # Keep paragraph breaks
                continue
            
            # Skip obvious UI elements (case-insensitive)
            lower_stripped = stripped.lower()
            if any(noise in lower_stripped for noise in [
                'open', 'bids', 'details', 'proposals', 'project details',
                'average bid', 'bidding ends', 'flag of', 'member since',
                'skills required', 'about the client', 'place a bid',
                'fixed-price', 'hourly', 'milestone'
            ]):
                # But allow if it's part of a longer sentence (not just a header)
                if len(stripped) < 40:
                    continue
            
            # Skip budget lines
            if re.match(r'^\$[\d,]+\.?\d*\s*[-–—]', stripped):
                continue
            
            # Skip single numbers (like bid counts)
            if re.match(r'^\d+$', stripped):
                continue
            
            # Skip very short lines (likely UI labels)
            if len(stripped) < 25:
                continue
            
            # Check if description starts
            if not description_started:
                for pattern in description_start_patterns:
                    if re.search(pattern, stripped, re.IGNORECASE):
                        description_started = True
                        description_lines.append(stripped)
                        break
            else:
                # We're in the description, keep adding until we hit a stop marker
                if any(stop in stripped for stop in ['Skills Required', 'About the Client']) and len(stripped) < 30:
                    break
                description_lines.append(stripped)
        
        if description_lines:
            # Join and clean up
            full_description = '\n\n'.join(description_lines).strip()
            # If we got at least 100 characters, it's probably valid
            if len(full_description) >= 100:
                return full_description
        
        # Enhanced fallback: try to find ANY substantial paragraph
        substantial_lines = []
        for line in lines:
            stripped = line.strip()
            # Find lines that are substantial (100+ chars) and don't look like UI
            if len(stripped) >= 100:
                lower = stripped.lower()
                # Skip if it's obviously UI noise
                if not any(noise in lower for noise in ['click here', 'sign up', 'login', 'register', 'browse', 'search']):
                    substantial_lines.append(stripped)
        
        if substantial_lines:
            return '\n\n'.join(substantial_lines[:3])  # Return first 3 substantial paragraphs
        
        # Last resort: return what we have with a note
        return "Unable to extract clean description. Please paste the FULL project page content starting from the project title."
    
    @staticmethod
    def _extract_budget(content: str) -> Optional[str]:
        """Extract budget range."""
        # Look for patterns like "$30.00 – 250.00 AUD"
        budget_pattern = r'\$[\d,]+\.?\d*\s*[-–—]\s*\$?[\d,]+\.?\d*\s*[A-Z]{3}'
        match = re.search(budget_pattern, content)
        if match:
            return match.group(0)
        
        # Look for "Average bid $XXX"
        avg_pattern = r'Average bid\s*\$[\d,]+\.?\d*\s*[A-Z]{3}'
        match = re.search(avg_pattern, content)
        if match:
            return match.group(0).replace('Average bid ', '')
        
        return None
    
    @staticmethod
    def _extract_bid_info(content: str) -> Dict[str, Any]:
        """Extract bid rank, total bids, average bid."""
        info = {}
        
        # Extract total bids - look for "Bids\n\n42" or "42 bids"
        bids_pattern = r'(?:Bids\s*\n+\s*(\d+)|(\d+)\s+bids?)'
        match = re.search(bids_pattern, content, re.IGNORECASE)
        if match:
            info['total'] = int(match.group(1) or match.group(2))
        
        # Extract average bid
        avg_pattern = r'Average bid\s*\$?([\d,]+\.?\d*)\s*([A-Z]{3})'
        match = re.search(avg_pattern, content)
        if match:
            info['average'] = f"${match.group(1)} {match.group(2)}"
        
        # Extract time remaining
        time_pattern = r'Bidding ends in\s+(.+?)(?:\n|$)'
        match = re.search(time_pattern, content)
        if match:
            info['time_remaining'] = match.group(1).strip()
        
        # Try to find current bid rank from "Your current bid will rank at #X"
        rank_pattern = r'rank at #(\d+)'
        match = re.search(rank_pattern, content)
        if match:
            info['rank'] = int(match.group(1))
        
        return info
    
    @staticmethod
    def _extract_client_info(content: str) -> Dict[str, str]:
        """Extract client location and rating."""
        info = {}
        
        # Extract location - usually before "Flag of COUNTRY"
        location_pattern = r'([\w\s]+)\s*Flag of\s+([A-Z]+)'
        match = re.search(location_pattern, content)
        if match:
            city = match.group(1).strip()
            country = match.group(2).strip()
            info['location'] = f"{city}, {country}"
        
        # Extract rating - look for pattern like "0.0" followed by review count
        rating_pattern = r'(\d+\.?\d*)\s*\n\s*(\d+)'
        match = re.search(rating_pattern, content)
        if match:
            rating = match.group(1)
            reviews = match.group(2)
            info['rating'] = f"{rating} ({reviews} reviews)"
        
        return info

    @staticmethod
    def _extract_skills(content: str) -> list[str]:
        """Extract required skills from content."""
        skills = []
        
        # Look for "Skills Required" section
        lines = content.split('\n')
        skills_section_found = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Found skills section
            if 'skills required' in stripped.lower() or 'skill required' in stripped.lower():
                skills_section_found = True
                # Get next few lines as skills
                for j in range(i + 1, min(i + 15, len(lines))):
                    skill_line = lines[j].strip()
                    # Stop if we hit another section
                    if any(stop in skill_line.lower() for stop in [
                        'about the client', 'project details', 'bids', 'average',
                        'bidding ends', 'member since', 'place a bid'
                    ]):
                        break
                    # Skip empty lines
                    if not skill_line or len(skill_line) < 2:
                        continue
                    # Skip lines that look like UI elements
                    if skill_line.lower() in ['open', 'details', 'proposals', 'fixed', 'hourly']:
                        continue
                    # Skip budget lines
                    if re.match(r'^\$[\d,]+', skill_line):
                        continue
                    # Add as skill if it's reasonable length
                    if 2 < len(skill_line) < 50:
                        skills.append(skill_line)
                
                break
        
        return skills[:10]  # Limit to 10 skills max
