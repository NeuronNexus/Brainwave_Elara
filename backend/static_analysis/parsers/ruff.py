"""
static_analysis/parsers/ruff.py

Parser for Ruff JSON output
"""
from typing import Dict, Any, List


def parse_ruff_output(data: List[Dict]) -> Dict[str, Any]:
    """
    Parse Ruff JSON output.
    
    Args:
        data: List of violation dictionaries from Ruff
        
    Returns:
        Structured dict with counts and top rules
    """
    errors = sum(1 for item in data if item.get("type") == "error")
    warnings = len(data) - errors
    files = len(set(item.get("filename", "") for item in data))
    
    rule_counts = {}
    for item in data:
        rule = item.get("code", "unknown")
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "errors": errors,
        "warnings": warnings,
        "files_affected": files,
        "total_issues": len(data),
        "top_rules": [rule for rule, _ in top_rules]
    }