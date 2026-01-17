"""
static_analysis/parsers/sonarjs.py

Parser for SonarJS (via ESLint plugin) output
"""
from typing import Dict, Any, List


def parse_sonarjs_output(data: List[Dict]) -> Dict[str, Any]:
    """
    Parse SonarJS output (ESLint with sonarjs plugin).
    
    Args:
        data: List of file results from ESLint with SonarJS rules
        
    Returns:
        Structured dict with bug patterns, code smells, and examples
    """
    bugs = 0
    code_smells = 0
    files_with_issues = 0
    sonar_rules = {}
    examples = []
    
    # SonarJS rules typically start with 'sonarjs/'
    for file_result in data:
        messages = file_result.get("messages", [])
        if messages:
            has_sonar_issue = False
            
        file_path = file_result.get("filePath", "")
        
        for msg in messages:
            rule = msg.get("ruleId", "")
            
            if rule and rule.startswith("sonarjs/"):
                has_sonar_issue = True
                sonar_rules[rule] = sonar_rules.get(rule, 0) + 1
                
                # Categorize by severity
                severity = msg.get("severity", 1)
                if severity == 2:
                    bugs += 1
                else:
                    code_smells += 1
                
                # Collect examples
                if len(examples) < 10:
                    examples.append({
                        "file": file_path.split("/")[-1] if "/" in file_path else file_path,
                        "line": msg.get("line"),
                        "rule": rule,
                        "message": msg.get("message", "")[:100],
                        "severity": "bug" if severity == 2 else "code_smell"
                    })
        
        if has_sonar_issue:
            files_with_issues += 1
    
    top_issues = sorted(sonar_rules.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "bugs": bugs,
        "code_smells": code_smells,
        "files_affected": files_with_issues,
        "total_issues": bugs + code_smells,
        "top_sonar_rules": [rule for rule, _ in top_issues],
        "examples": examples
    }