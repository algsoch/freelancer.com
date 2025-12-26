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
        
        return ParsedProject(
            project_name=project_name,
            project_description=project_description,
            budget_range=budget_range,
            bid_rank=bid_info.get('rank'),
            total_bids=bid_info.get('total'),
            average_bid=bid_info.get('average'),
            time_remaining=bid_info.get('time_remaining'),
            client_location=client_info.get('location'),
            client_rating=client_info.get('rating')
        )
    
    @staticmethod
    def _extract_project_name(content: str) -> Optional[str]:
        """Extract project title/name."""
        lines = content.strip().split('\n')
        # Usually the first significant line
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('$'):
                # Skip common headers
                if line.lower() not in ['open', 'bids', 'details', 'proposals', 'project details']:
                    return line
        return None
    
    @staticmethod
    def _extract_description(content: str) -> str:
        """Extract the main project description."""
        # Look for the main paragraph(s) with project requirements
        # Usually between budget info and deliverables/skills
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Find paragraphs that look like project description
        description_parts = []
        in_description = False
        
        for para in paragraphs:
            # Skip headers and short lines
            if len(para) < 50:
                continue
            
            # Look for description keywords
            if any(keyword in para.lower() for keyword in [
                'i\'m', 'i am', 'we need', 'looking for', 'project', 'requirement',
                'need a', 'need an', 'key points', 'deliverables', 'must', 'should'
            ]):
                in_description = True
                description_parts.append(para)
            elif in_description and not any(stop in para.lower() for stop in [
                'skills required', 'about the client', 'place a bid', 'your bid',
                'bid amount', 'member since', 'clarification'
            ]):
                description_parts.append(para)
            elif in_description and any(stop in para.lower() for stop in [
                'skills required', 'about the client'
            ]):
                break
        
        return '\n\n'.join(description_parts) if description_parts else content[:1000]
    
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
