"""
static_analysis/parsers/semgrep.py

Parser for Semgrep JSON output
"""
from typing import Dict, Any


def parse_semgrep_output(data: Dict) -> Dict[str, Any]:
    """
    Parse Semgrep JSON output.
    
    Args:
        data: Semgrep results dictionary
        
    Returns:
        Structured dict with vulnerability counts by severity and examples
    """
    results = data.get("results", [])
    
    severity_counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    security_issues = 0
    examples = []
    
    for finding in results:
        extra = finding.get("extra", {})
        severity = extra.get("severity", "INFO")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count security-related findings
        metadata = extra.get("metadata", {})
        if "security" in str(metadata).lower():
            security_issues += 1
        
        # Collect examples
        if len(examples) < 10:
            path = finding.get("path", "")
            examples.append({
                "file": path.split("/")[-1] if "/" in path else path,
                "line": finding.get("start", {}).get("line"),
                "rule": extra.get("message", "")[:100],
                "severity": severity.lower()
            })
    
    return {
        "vulnerabilities": len(results),
        "severity": severity_counts,
        "high_severity": severity_counts.get("ERROR", 0),
        "security_issues": security_issues,
        "files_affected": len(set(r.get("path", "") for r in results)),
        "examples": examples
    }