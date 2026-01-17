"""
static_analysis/parsers/eslint.py

Parser for ESLint JSON output
"""
from typing import Dict, Any, List


def parse_eslint_output(data: List[Dict]) -> Dict[str, Any]:
    """
    Parse ESLint JSON output.
    
    Args:
        data: List of file results from ESLint
        
    Returns:
        Structured dict with error/warning counts, top rules, and examples
    """
    total_errors = 0
    total_warnings = 0
    files_with_issues = 0
    rule_counts = {}
    complexity_issues = 0
    examples = []
    
    for file_result in data:
        messages = file_result.get("messages", [])
        if messages:
            files_with_issues += 1
        
        file_path = file_result.get("filePath", "")
        
        for msg in messages:
            severity = msg.get("severity", 1)
            if severity == 2:
                total_errors += 1
            else:
                total_warnings += 1
            
            rule = msg.get("ruleId", "unknown")
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
            
            if rule and "complexity" in rule.lower():
                complexity_issues += 1
            
            # Collect examples (first few issues)
            if len(examples) < 10:
                examples.append({
                    "file": file_path.split("/")[-1] if "/" in file_path else file_path,
                    "line": msg.get("line"),
                    "rule": rule,
                    "message": msg.get("message", "")[:100],
                    "severity": "error" if severity == 2 else "warning"
                })
    
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "errors": total_errors,
        "warnings": total_warnings,
        "files_affected": files_with_issues,
        "total_issues": total_errors + total_warnings,
        "top_rules": [rule for rule, _ in top_rules],
        "complexity_violations": complexity_issues,
        "examples": examples
    }