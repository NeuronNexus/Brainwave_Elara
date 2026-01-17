"""
static_analysis/parsers/bandit.py

Parser for Bandit JSON output
"""
from typing import Dict, Any


def parse_bandit_output(data: Dict) -> Dict[str, Any]:
    """
    Parse Bandit JSON output.
    
    Args:
        data: Bandit results dictionary
        
    Returns:
        Structured dict with vulnerability counts by severity
    """
    results = data.get("results", [])
    
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for issue in results:
        severity = issue.get("issue_severity", "LOW")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        "vulnerabilities": len(results),
        "severity": severity_counts,
        "high_severity": severity_counts["HIGH"],
        "files_affected": len(set(r.get("filename", "") for r in results))
    }