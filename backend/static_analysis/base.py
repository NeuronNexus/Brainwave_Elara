"""
static_analysis/base.py

Base contract for all static analyzers.
Defines the interface that Python, JavaScript, and other analyzers must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Standard container for tool execution results."""
    tool: str
    status: str  # "ok", "failed", "skipped"
    reason: Optional[str] = None
    raw_output: Optional[Dict] = None
    parsed_output: Optional[Dict] = None


class StaticAnalyzer(ABC):
    """
    Base class for all static analyzers.
    Each language/ecosystem gets its own implementation.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.pre_scan = {}
        self.ai_pre_analysis = {}
        self.tool_results: List[ToolResult] = []
        self.errors: List[str] = []
        
    @abstractmethod
    def configure(self, pre_scan: Dict[str, Any], ai_pre_analysis: Dict[str, Any]) -> None:
        """
        Configure analyzer based on pre-scan and AI analysis.
        Determines:
        - Which tools to run
        - Which folders to scan
        - Which files to exclude
        """
        pass
    
    @abstractmethod
    def run_tools(self) -> List[ToolResult]:
        """
        Execute all configured tools.
        Each tool runs in isolated process with timeout.
        Never crashes pipeline - returns ToolResult with status.
        """
        pass
    
    @abstractmethod
    def parse_results(self) -> Dict[str, Any]:
        """
        Parse raw tool outputs into standardized format.
        Each tool has its own parser logic.
        """
        pass
    
    @abstractmethod
    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed results into universal schema:
        {
          "syntax": {...},
          "style": {...},
          "bugs": {...},
          "security": {...},
          "complexity": {...}
        }
        """
        pass
    
    def output(self) -> Dict[str, Any]:
        """
        Final output contract - same across all analyzers.
        """
        parsed = self.parse_results()
        normalized = self.normalize(parsed)
        
        return {
            "language": self._get_language(),
            "toolchain": [tr.tool for tr in self.tool_results if tr.status == "ok"],
            "results": normalized,
            "tool_status": {
                tr.tool: tr.status for tr in self.tool_results
            },
            "errors": self.errors
        }
    
    @abstractmethod
    def _get_language(self) -> str:
        """Return the language this analyzer handles."""
        pass
    
    def _get_scan_paths(self) -> List[str]:
        """
        Determine which paths to scan based on configuration.
        Excludes common noise directories.
        """
        # Default to root, but subclasses can override
        return [self.repo_path]
    
    def _get_exclude_patterns(self) -> List[str]:
        """
        Get patterns to exclude from scanning.
        Based on pre_scan data and language conventions.
        """
        base_excludes = [
            ".git", "__pycache__", "node_modules", "venv", ".venv",
            ".idea", ".vscode", "dist", "build", ".next", "target",
            "bin", "obj", "*.min.js", "*.bundle.js"
        ]
        return base_excludes