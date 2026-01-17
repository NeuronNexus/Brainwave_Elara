"""
static_analysis/parsers/radon.py

Parser for Radon JSON output
"""
from typing import Dict, Any


def parse_radon_output(data: Dict) -> Dict[str, Any]:
    """
    Parse Radon complexity JSON output.
    
    Args:
        data: Dictionary mapping file paths to function complexity data
        
    Returns:
        Structured dict with complexity metrics
    """
    complexities = []
    high_complexity = 0
    
    for file_path, functions in data.items():
        for func in functions:
            complexity = func.get("complexity", 0)
            complexities.append(complexity)
            if complexity > 10:
                high_complexity += 1
    
    avg = sum(complexities) / len(complexities) if complexities else 0
    
    return {
        "average_complexity": round(avg, 2),
        "high_complexity_count": high_complexity,
        "total_functions": len(complexities),
        "max_complexity": max(complexities) if complexities else 0
    }