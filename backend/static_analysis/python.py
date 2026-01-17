"""
static_analysis/python.py

Python Static Analyzer
Toolchain: Ruff, Bandit, Radon, Vulture
"""
import os
import json
import subprocess
import tempfile
from typing import Dict, Any, List
from static_analysis.base import StaticAnalyzer, ToolResult
from static_analysis.parsers.ruff import parse_ruff_output
from static_analysis.parsers.bandit import parse_bandit_output
from static_analysis.parsers.radon import parse_radon_output
from static_analysis.parsers.vulture import parse_vulture_output
import logging

logger = logging.getLogger(__name__)


class PythonAnalyzer(StaticAnalyzer):
    
    def _get_language(self) -> str:
        return "Python"
    
    def configure(self, pre_scan: Dict[str, Any], ai_pre_analysis: Dict[str, Any]) -> None:
        """Configure Python-specific analysis."""
        self.pre_scan = pre_scan
        self.ai_pre_analysis = ai_pre_analysis
        
        # Determine scan targets
        extensions = pre_scan.get("tech_signals", {}).get("extensions", {})
        self.python_file_count = extensions.get(".py", 0)
        
        logger.info(f"Python analyzer configured: {self.python_file_count} .py files found")
    
    def run_tools(self) -> List[ToolResult]:
        """Execute Python toolchain."""
        self.tool_results = []
        
        # Tool order: fast to slow
        self.tool_results.append(self._run_ruff())
        self.tool_results.append(self._run_bandit())
        self.tool_results.append(self._run_radon())
        self.tool_results.append(self._run_vulture())
        
        return self.tool_results
    
    def _run_ruff(self) -> ToolResult:
        """Run Ruff for linting and style checks."""
        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json", self.repo_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Ruff returns non-zero on violations, which is expected
            if result.stdout:
                data = json.loads(result.stdout)
                return ToolResult(
                    tool="ruff",
                    status="ok",
                    raw_output=data,
                    parsed_output=parse_ruff_output(data)
                )
            else:
                return ToolResult(
                    tool="ruff",
                    status="ok",
                    raw_output=[],
                    parsed_output={"errors": 0, "warnings": 0, "files_affected": 0}
                )
                
        except FileNotFoundError:
            return ToolResult(tool="ruff", status="failed", reason="not installed")
        except subprocess.TimeoutExpired:
            return ToolResult(tool="ruff", status="failed", reason="timeout")
        except Exception as e:
            return ToolResult(tool="ruff", status="failed", reason=str(e))
    
    def _run_bandit(self) -> ToolResult:
        """Run Bandit for security analysis."""
        try:
            result = subprocess.run(
                ["bandit", "-r", self.repo_path, "-f", "json", "-ll"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                return ToolResult(
                    tool="bandit",
                    status="ok",
                    raw_output=data,
                    parsed_output=parse_bandit_output(data)
                )
            else:
                return ToolResult(
                    tool="bandit",
                    status="ok",
                    raw_output={},
                    parsed_output={"vulnerabilities": 0, "severity": {}}
                )
                
        except FileNotFoundError:
            return ToolResult(tool="bandit", status="failed", reason="not installed")
        except subprocess.TimeoutExpired:
            return ToolResult(tool="bandit", status="failed", reason="timeout")
        except Exception as e:
            return ToolResult(tool="bandit", status="failed", reason=str(e))
    
    def _run_radon(self) -> ToolResult:
        """Run Radon for complexity analysis."""
        try:
            # Run cyclomatic complexity
            result = subprocess.run(
                ["radon", "cc", self.repo_path, "-j"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                return ToolResult(
                    tool="radon",
                    status="ok",
                    raw_output=data,
                    parsed_output=parse_radon_output(data)
                )
            else:
                return ToolResult(
                    tool="radon",
                    status="ok",
                    raw_output={},
                    parsed_output={"average_complexity": 0, "high_complexity_count": 0}
                )
                
        except FileNotFoundError:
            return ToolResult(tool="radon", status="failed", reason="not installed")
        except subprocess.TimeoutExpired:
            return ToolResult(tool="radon", status="failed", reason="timeout")
        except Exception as e:
            return ToolResult(tool="radon", status="failed", reason=str(e))
    
    def _run_vulture(self) -> ToolResult:
        """Run Vulture for dead code detection."""
        try:
            result = subprocess.run(
                ["vulture", self.repo_path, "--min-confidence", "80"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse line-based output
            dead_code_items = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('#'):
                        dead_code_items.append(line)
            
            return ToolResult(
                tool="vulture",
                status="ok",
                raw_output={"items": dead_code_items},
                parsed_output=parse_vulture_output(dead_code_items)
            )
                
        except FileNotFoundError:
            return ToolResult(tool="vulture", status="failed", reason="not installed")
        except subprocess.TimeoutExpired:
            return ToolResult(tool="vulture", status="failed", reason="timeout")
        except Exception as e:
            return ToolResult(tool="vulture", status="failed", reason=str(e))
    
    def parse_results(self) -> Dict[str, Any]:
        """Aggregate all parsed results."""
        parsed = {}
        for tr in self.tool_results:
            if tr.status == "ok" and tr.parsed_output:
                parsed[tr.tool] = tr.parsed_output
        return parsed
    
    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to universal schema with status indicators."""
        ruff = parsed_data.get("ruff", {})
        bandit = parsed_data.get("bandit", {})
        radon = parsed_data.get("radon", {})
        vulture = parsed_data.get("vulture", {})
        
        # Check which tools actually ran
        ruff_ran = "ruff" in [tr.tool for tr in self.tool_results if tr.status == "ok"]
        bandit_ran = "bandit" in [tr.tool for tr in self.tool_results if tr.status == "ok"]
        radon_ran = "radon" in [tr.tool for tr in self.tool_results if tr.status == "ok"]
        vulture_ran = "vulture" in [tr.tool for tr in self.tool_results if tr.status == "ok"]
        
        return {
            "syntax": {
                "errors": ruff.get("errors", 0) if ruff_ran else None,
                "files_affected": ruff.get("files_affected", 0) if ruff_ran else None,
                "status": "analyzed" if ruff_ran else "not_analyzed",
                "reason": None if ruff_ran else "ruff_failed"
            },
            "style": {
                "warnings": ruff.get("warnings", 0) if ruff_ran else None,
                "top_violations": ruff.get("top_rules", [])[:5] if ruff_ran else [],
                "status": "analyzed" if ruff_ran else "not_analyzed"
            },
            "bugs": {
                "potential_bugs": 0,
                "dead_code": vulture.get("dead_code_count", 0) if vulture_ran else None,
                "status": "analyzed" if vulture_ran else "not_analyzed"
            },
            "security": {
                "vulnerabilities": bandit.get("vulnerabilities", 0) if bandit_ran else None,
                "high_severity": bandit.get("high_severity", 0) if bandit_ran else None,
                "severity_breakdown": bandit.get("severity", {}) if bandit_ran else {},
                "status": "analyzed" if bandit_ran else "not_analyzed",
                "reason": None if bandit_ran else "bandit_failed"
            },
            "complexity": {
                "average": radon.get("average_complexity", 0) if radon_ran else None,
                "high_complexity_functions": radon.get("high_complexity_count", 0) if radon_ran else None,
                "max_complexity": radon.get("max_complexity", 0) if radon_ran else None,
                "status": "analyzed" if radon_ran else "not_analyzed"
            }
        }