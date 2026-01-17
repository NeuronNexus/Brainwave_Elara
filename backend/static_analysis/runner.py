"""
static_analysis/runner.py

Static Analysis Runner
Routes to appropriate analyzers based on pre_scan and ai_pre_analysis.
Handles full-stack projects by running multiple analyzers.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from static_analysis.base import StaticAnalyzer
from static_analysis.python import PythonAnalyzer
from static_analysis.javascript import JavaScriptAnalyzer

logger = logging.getLogger(__name__)


class StaticAnalysisRunner:
    """
    Orchestrates static analysis execution.
    Determines which analyzers to run and merges results.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.pre_scan = {}
        self.ai_pre_analysis = {}
    
    def configure(self, pre_scan: Dict[str, Any], ai_pre_analysis: Dict[str, Any]) -> None:
        """Store configuration for routing decisions."""
        self.pre_scan = pre_scan
        self.ai_pre_analysis = ai_pre_analysis
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution method.
        Routes to appropriate analyzers and returns unified results.
        """
        # Determine project type
        language = self.ai_pre_analysis.get("language", "").lower()
        app_type = self.ai_pre_analysis.get("app_type", "").lower()
        
        logger.info(f"Static analysis starting - Language: {language}, Type: {app_type}")
        
        # Check if full-stack
        if "full" in app_type or "fullstack" in app_type or "full-stack" in app_type:
            return self._run_fullstack_analysis()
        
        # Single language/ecosystem
        analyzer = self._select_analyzer(language)
        
        if analyzer is None:
            return self._empty_result(f"No analyzer available for language: {language}")
        
        return self._run_single_analyzer(analyzer)
    
    def _run_single_analyzer(self, analyzer: StaticAnalyzer) -> Dict[str, Any]:
        """Execute a single analyzer and return its output."""
        try:
            analyzer.configure(self.pre_scan, self.ai_pre_analysis)
            analyzer.run_tools()
            result = analyzer.output()
            
            logger.info(f"Static analysis completed: {result['language']}")
            return result
            
        except Exception as e:
            logger.error(f"Static analysis failed: {e}")
            return self._empty_result(f"Analysis failed: {str(e)}")
    
    def _run_fullstack_analysis(self) -> Dict[str, Any]:
        """
        Handle full-stack projects.
        Detects frontend/backend folders and runs appropriate analyzers.
        """
        logger.info("Detected full-stack project - analyzing frontend and backend")
        
        # Detect frontend/backend directories
        frontend_path = self._detect_frontend_dir()
        backend_path = self._detect_backend_dir()
        
        results = {
            "project_type": "full-stack",
            "frontend_analysis": None,
            "backend_analysis": None,
            "errors": []
        }
        
        # Analyze frontend if found
        if frontend_path:
            logger.info(f"Analyzing frontend at: {frontend_path}")
            frontend_analyzer = JavaScriptAnalyzer(frontend_path)
            try:
                frontend_analyzer.configure(self.pre_scan, self.ai_pre_analysis)
                frontend_analyzer.run_tools()
                results["frontend_analysis"] = frontend_analyzer.output()
            except Exception as e:
                logger.error(f"Frontend analysis failed: {e}")
                results["errors"].append(f"Frontend: {str(e)}")
        
        # Analyze backend if found
        if backend_path:
            logger.info(f"Analyzing backend at: {backend_path}")
            backend_analyzer = self._select_analyzer_for_path(backend_path)
            if backend_analyzer:
                try:
                    backend_analyzer.configure(self.pre_scan, self.ai_pre_analysis)
                    backend_analyzer.run_tools()
                    results["backend_analysis"] = backend_analyzer.output()
                except Exception as e:
                    logger.error(f"Backend analysis failed: {e}")
                    results["errors"].append(f"Backend: {str(e)}")
        
        return results
    
    def _select_analyzer(self, language: str) -> Optional[StaticAnalyzer]:
        """Select appropriate analyzer based on language."""
        if "python" in language:
            return PythonAnalyzer(self.repo_path)
        elif "javascript" in language or "typescript" in language or "js" in language or "ts" in language:
            return JavaScriptAnalyzer(self.repo_path)
        else:
            logger.warning(f"No analyzer available for language: {language}")
            return None
    
    def _select_analyzer_for_path(self, path: str) -> Optional[StaticAnalyzer]:
        """Select analyzer based on files in a specific path."""
        # Quick check for dominant file types
        extensions = {}
        for root, dirs, files in os.walk(path):
            # Skip node_modules, venv, etc.
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', 'venv', '__pycache__'}]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
        
        # Determine language by file count
        py_count = extensions.get(".py", 0)
        js_count = extensions.get(".js", 0) + extensions.get(".ts", 0)
        
        if py_count > js_count:
            return PythonAnalyzer(path)
        elif js_count > 0:
            return JavaScriptAnalyzer(path)
        else:
            return None
    
    def _detect_frontend_dir(self) -> Optional[str]:
        """Attempt to detect frontend directory."""
        candidates = ["client", "frontend", "web", "public", "app", "src/client"]
        
        for candidate in candidates:
            path = os.path.join(self.repo_path, candidate)
            if os.path.isdir(path):
                # Check if it has JS/TS files
                has_js = self._has_files_with_ext(path, [".js", ".jsx", ".ts", ".tsx"])
                if has_js:
                    return path
        
        return None
    
    def _detect_backend_dir(self) -> Optional[str]:
        """Attempt to detect backend directory."""
        candidates = ["server", "backend", "api", "src/server"]
        
        for candidate in candidates:
            path = os.path.join(self.repo_path, candidate)
            if os.path.isdir(path):
                return path
        
        # If no explicit backend dir, assume root
        return self.repo_path
    
    def _has_files_with_ext(self, path: str, extensions: List[str]) -> bool:
        """Check if directory contains files with given extensions."""
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', 'venv'}]
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    return True
        return False
    
    def _empty_result(self, error_msg: str) -> Dict[str, Any]:
        """Return empty result with error message."""
        return {
            "language": "Unknown",
            "toolchain": [],
            "results": {
                "syntax": {},
                "style": {},
                "bugs": {},
                "security": {},
                "complexity": {}
            },
            "tool_status": {},
            "errors": [error_msg]
        }


def run_static_analysis(
    repo_path: str,
    pre_scan: Dict[str, Any],
    ai_pre_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function for running static analysis.
    
    Args:
        repo_path: Path to repository
        pre_scan: Results from prescan.py
        ai_pre_analysis: Results from Gemini analysis
    
    Returns:
        Static analysis results in universal schema
    """
    runner = StaticAnalysisRunner(repo_path)
    runner.configure(pre_scan, ai_pre_analysis)
    return runner.run()