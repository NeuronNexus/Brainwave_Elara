"""
static_analysis/javascript.py
Elite Edition: Pinned Dependencies for Stability
"""
import os
import json
import subprocess
import shutil
from typing import Dict, Any, List, Optional
from static_analysis.base import StaticAnalyzer, ToolResult
from static_analysis.parsers.eslint import parse_eslint_output
from static_analysis.parsers.sonarjs import parse_sonarjs_output
from static_analysis.parsers.semgrep import parse_semgrep_output
import logging

logger = logging.getLogger(__name__)

class JavaScriptAnalyzer(StaticAnalyzer):
    
    def _get_language(self) -> str:
        return "JavaScript"
    
    def configure(self, pre_scan: Dict[str, Any], ai_pre_analysis: Dict[str, Any]) -> None:
        self.pre_scan = pre_scan
        self.ai_pre_analysis = ai_pre_analysis
        
        extensions = pre_scan.get("tech_signals", {}).get("extensions", {})
        self.total_files = sum(extensions.get(k, 0) for k in [".js", ".ts", ".jsx", ".tsx"])
        logger.info(f"JS/TS analyzer configured: {self.total_files} files found")
        
        self._install_analysis_tools()

    def _resolve_binary(self, binary_name: str, local_path: Optional[str] = None) -> str:
        if local_path:
            abs_path = os.path.abspath(local_path)
            if os.name == 'nt':
                for ext in ['.cmd', '.ps1', '.exe', '']:
                    candidate = abs_path + ext
                    if os.path.exists(candidate):
                        return candidate
            elif os.path.exists(abs_path):
                return abs_path

        global_bin = shutil.which(binary_name)
        if global_bin: return global_bin
        return binary_name

    def _install_analysis_tools(self):
        if not os.path.exists(os.path.join(self.repo_path, "package.json")):
            return

        logger.info("Injecting analysis tools (ESLint v8 + SonarJS)...")
        npm_cmd = self._resolve_binary("npm")
        
        try:
            # FIX: PIN ESLINT TO v8.56.0 TO SUPPORT --no-eslintrc FLAG
            # ESLint v9 removed this flag, causing the previous crash.
            subprocess.run(
                [
                    npm_cmd, "install", 
                    "eslint@8.56.0", "eslint-plugin-sonarjs@0.23.0", 
                    "--no-save", 
                    "--legacy-peer-deps", 
                    "--no-audit", 
                    "--no-fund"
                ],
                cwd=self.repo_path,
                check=True,
                timeout=300,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Tool injection failed: {e.stderr.decode('utf-8', errors='ignore')[:200]}")
        except Exception as e:
            logger.warning(f"Tool injection crashed: {str(e)}")

    def run_tools(self) -> List[ToolResult]:
        self.tool_results = []
        self.tool_results.append(self._run_eslint())
        self.tool_results.append(self._run_sonarjs())
        self.tool_results.append(self._run_semgrep())
        return self.tool_results
    
    def _run_eslint(self) -> ToolResult:
        try:
            local_bin = os.path.join(self.repo_path, "node_modules", ".bin", "eslint")
            eslint_cmd = self._resolve_binary("eslint", local_bin)
            config_path = self._generate_eslint_config()
            
            # Check for binary existence to give clear error
            if "node_modules" in eslint_cmd and not os.path.exists(eslint_cmd.split('.cmd')[0] if os.name == 'nt' else eslint_cmd):
                 return ToolResult("eslint", "failed", reason="binary_missing_after_install")

            result = subprocess.run(
                [
                    eslint_cmd, 
                    "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", 
                    "--format=json", 
                    "-c", config_path, 
                    "--no-eslintrc" 
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout and result.stdout.strip().startswith("["):
                data = json.loads(result.stdout)
                return ToolResult("eslint", "ok", raw_output=data, parsed_output=parse_eslint_output(data))
            
            if result.returncode == 0 and not result.stdout.strip():
                 return ToolResult("eslint", "ok", raw_output=[], parsed_output={"errors": 0, "warnings": 0, "files_affected": 0})

            # Return the CLI error from stderr
            err = result.stderr[:200] if result.stderr else "unknown_cli_error"
            return ToolResult("eslint", "failed", reason=f"cli_error: {err}")
                
        except subprocess.TimeoutExpired:
            return ToolResult("eslint", "failed", reason="timeout")
        except Exception as e:
            return ToolResult("eslint", "failed", reason=str(e))
    
    def _run_sonarjs(self) -> ToolResult:
        try:
            local_bin = os.path.join(self.repo_path, "node_modules", ".bin", "eslint")
            eslint_cmd = self._resolve_binary("eslint", local_bin)
            config_path = self._generate_sonarjs_config()
            
            result = subprocess.run(
                [
                    eslint_cmd, 
                    "**/*.js", "**/*.jsx", 
                    "--format=json", 
                    "-c", config_path, 
                    "--no-eslintrc"
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout and result.stdout.strip().startswith("["):
                data = json.loads(result.stdout)
                return ToolResult("sonarjs", "ok", raw_output=data, parsed_output=parse_sonarjs_output(data))
            
            if result.returncode == 0:
                 return ToolResult("sonarjs", "ok", raw_output=[], parsed_output={"bugs": 0, "code_smells": 0})

            return ToolResult("sonarjs", "failed", reason="cli_error")
        except Exception as e:
            return ToolResult("sonarjs", "failed", reason=str(e))
    
    def _run_semgrep(self) -> ToolResult:
        try:
            semgrep_cmd = self._resolve_binary("semgrep")
            result = subprocess.run(
                [semgrep_cmd, "--config=auto", "--json", "--metrics=off", self.repo_path],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.stdout:
                data = json.loads(result.stdout)
                return ToolResult("semgrep", "ok", raw_output=data, parsed_output=parse_semgrep_output(data))
            return ToolResult("semgrep", "ok", raw_output={}, parsed_output={})
        except Exception as e:
            return ToolResult("semgrep", "failed", reason=str(e))

    def _generate_eslint_config(self) -> str:
        config = {
            "env": {"browser": True, "es2021": True, "node": True},
            "extends": "eslint:recommended",
            "parserOptions": {"ecmaVersion": "latest", "sourceType": "module", "ecmaFeatures": {"jsx": True}},
            "rules": {"complexity": ["warn", 10], "max-depth": ["warn", 4], "no-unused-vars": "warn", "no-console": "off"}
        }
        path = os.path.join(self.repo_path, ".eslintrc.analysis.json")
        with open(path, 'w') as f: json.dump(config, f)
        return path
    
    def _generate_sonarjs_config(self) -> str:
        config = {
            "env": {"browser": True, "es2021": True, "node": True},
            "extends": "eslint:recommended",
            "rules": {"no-unreachable": "error", "no-constant-condition": "error", "no-dupe-keys": "error", "eqeqeq": "warn"}
        }
        path = os.path.join(self.repo_path, ".eslintrc.sonar.json")
        with open(path, 'w') as f: json.dump(config, f)
        return path

    def parse_results(self) -> Dict[str, Any]:
        parsed = {}
        for tr in self.tool_results:
            if tr.status == "ok" and tr.parsed_output is not None:
                parsed[tr.tool] = tr.parsed_output
        return parsed
    
    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        def get_tool(name): return next((tr for tr in self.tool_results if tr.tool == name), None)
        tr_eslint, tr_sonar, tr_semgrep = get_tool("eslint"), get_tool("sonarjs"), get_tool("semgrep")
        
        eslint_ok = tr_eslint and tr_eslint.status == "ok"
        sonar_ok = tr_sonar and tr_sonar.status == "ok"
        semgrep_ok = tr_semgrep and tr_semgrep.status == "ok"
        
        d_eslint = parsed_data.get("eslint", {})
        d_sonar = parsed_data.get("sonarjs", {})
        d_semgrep = parsed_data.get("semgrep", {})
        
        return {
            "syntax": {
                "errors": d_eslint.get("errors", 0) if eslint_ok else None,
                "files_affected": d_eslint.get("files_affected", 0) if eslint_ok else None,
                "status": "analyzed" if eslint_ok else "not_analyzed",
                "reason": None if eslint_ok else (tr_eslint.reason if tr_eslint else "tool_missing"),
                "examples": d_eslint.get("examples", [])[:3] if eslint_ok else []
            },
            "style": {
                "warnings": d_eslint.get("warnings", 0) if eslint_ok else None,
                "top_violations": d_eslint.get("top_rules", [])[:5] if eslint_ok else [],
                "status": "analyzed" if eslint_ok else "not_analyzed"
            },
            "bugs": {
                "potential_bugs": d_sonar.get("bugs", 0) if sonar_ok else None,
                "code_smells": d_sonar.get("code_smells", 0) if sonar_ok else None,
                "dead_code": 0,
                "status": "analyzed" if sonar_ok else "not_analyzed",
                "reason": None if sonar_ok else (tr_sonar.reason if tr_sonar else "tool_missing"),
                "examples": d_sonar.get("examples", [])[:3] if sonar_ok else []
            },
            "security": {
                "vulnerabilities": d_semgrep.get("vulnerabilities", 0) if semgrep_ok else None,
                "high_severity": d_semgrep.get("high_severity", 0) if semgrep_ok else None,
                "severity_breakdown": d_semgrep.get("severity", {}) if semgrep_ok else {},
                "status": "analyzed" if semgrep_ok else "not_analyzed",
                "examples": d_semgrep.get("examples", [])[:3] if semgrep_ok else []
            },
            "complexity": {
                "violations": d_eslint.get("complexity_violations", 0) if eslint_ok else None,
                "files_with_issues": d_eslint.get("files_affected", 0) if eslint_ok else None,
                "status": "analyzed" if eslint_ok else "not_analyzed"
            }
        }