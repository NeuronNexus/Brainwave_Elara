"""
static_analysis/parsers/vulture.py

Parser for Vulture output
"""
from typing import Dict, Any, List


def parse_vulture_output(items: List[str]) -> Dict[str, Any]:
    """
    Parse Vulture line-based output.
    
    Args:
        items: List of dead code detection lines from Vulture
        
    Returns:
        Structured dict with dead code counts
    """
    return {
        "dead_code_count": len(items),
        "has_dead_code": len(items) > 0,
        "items": items[:10]  # Include first 10 for reference
    }