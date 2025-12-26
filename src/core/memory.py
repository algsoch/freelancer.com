"""Memory and session management for learning from past bids."""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class BidMemory:
    """Manages bid history and learning from past performance."""
    
    def __init__(self, storage_file: str = ".bid_history.json"):
        """Initialize bid memory with storage file."""
        self.storage_file = Path(storage_file)
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load bid history from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save bid history to storage."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving history: {e}")
    
    def add_bid(self, project_name: str, project_description: str, 
                generated_bid: str, total_bids: Optional[int] = None,
                budget_range: Optional[str] = None, won: Optional[bool] = None):
        """Add a new bid to history."""
        bid_entry = {
            "timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "project_description": project_description[:500],  # Truncate for storage
            "generated_bid": generated_bid,
            "total_bids": total_bids,
            "budget_range": budget_range,
            "won": won,  # None = pending, True = won, False = lost
        }
        self.history.append(bid_entry)
        self._save_history()
    
    def get_recent_bids(self, limit: int = 10) -> List[Dict]:
        """Get recent bids for context."""
        return self.history[-limit:]
    
    def get_winning_patterns(self) -> Dict:
        """Analyze winning bids to find patterns."""
        won_bids = [b for b in self.history if b.get("won") is True]
        lost_bids = [b for b in self.history if b.get("won") is False]
        
        return {
            "total_bids": len(self.history),
            "won_count": len(won_bids),
            "lost_count": len(lost_bids),
            "win_rate": len(won_bids) / len(self.history) if self.history else 0,
            "recent_wins": won_bids[-5:] if won_bids else [],
        }
    
    def get_context_for_generation(self) -> str:
        """Get context string to improve bid generation."""
        if len(self.history) < 3:
            return ""
        
        patterns = self.get_winning_patterns()
        recent = self.get_recent_bids(5)
        
        context = f"\n\n📊 LEARNING FROM PAST BIDS:\n"
        context += f"- Total bids submitted: {patterns['total_bids']}\n"
        
        if patterns['won_count'] > 0:
            context += f"- Success rate: {patterns['win_rate']:.1%}\n"
            context += f"- Winning bids: {patterns['won_count']}\n\n"
            context += "Recent successful approaches:\n"
            for bid in patterns['recent_wins'][-3:]:
                context += f"  • Project: {bid['project_name'][:50]}...\n"
                context += f"    Approach: {bid['generated_bid'][:150]}...\n\n"
        
        return context
    
    def update_bid_result(self, project_name: str, won: bool):
        """Update whether a bid was won or lost."""
        for bid in reversed(self.history):
            if bid["project_name"] == project_name and bid.get("won") is None:
                bid["won"] = won
                self._save_history()
                break
    
    def get_stats(self) -> Dict:
        """Get statistics for display."""
        patterns = self.get_winning_patterns()
        return {
            "total_bids": patterns["total_bids"],
            "won": patterns["won_count"],
            "lost": patterns["lost_count"],
            "pending": patterns["total_bids"] - patterns["won_count"] - patterns["lost_count"],
            "win_rate": f"{patterns['win_rate']:.1%}" if patterns['total_bids'] > 0 else "N/A"
        }


# Global memory instance
bid_memory = BidMemory()
