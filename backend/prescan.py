import os
import re
from collections import defaultdict
from typing import Dict, List, Any, Set

class PreScanner:
    """
    Deterministic Intelligence Layer.
    measures, enumerates, and verifies repository content without AI inference.
    """

    # ------------------------------------------------------------------
    # CONFIGURATION & PATTERNS
    # ------------------------------------------------------------------
    IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode', 'dist', 'build', '.next', 'target', 'bin', 'obj'}
    
    # Categorization Rules
    CONFIG_FILES = {
        'package.json', 'tsconfig.json', 'pyproject.toml', 'requirements.txt', 'gemfile', 
        'composer.json', 'pom.xml', 'build.gradle', 'go.mod', 'cargo.toml', 'dockerfile', 
        'docker-compose.yml', 'makefile', 'jenkinsfile', '.gitlab-ci.yml', 'azure-pipelines.yml'
    }
    
    TEST_INDICATORS = {'test', 'spec', 'tests', '__tests__', 'unittest', 'pytest'}
    
    # Lightweight Regex for Secrets (High confidence patterns only to avoid noise)
    SECRET_PATTERNS = {
        "aws_key": re.compile(r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'),
        "generic_private_key": re.compile(r'-----BEGIN ((EC|PGP|DSA|RSA|OPENSSH) )?PRIVATE KEY-----'),
        "generic_token": re.compile(r'(api[_-]?key|auth[_-]?token|access[_-]?token)[ \t]*[:=][ \t]*[\'"][a-zA-Z0-9_\-]{20,}[\'"]', re.IGNORECASE)
    }

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.stats = {
            "extensions": defaultdict(int),
            "file_count": 0,
            "dir_count": 0,
            "total_size_kb": 0,
            "depth": 0,
            "config_files": [],
            "test_files": [],
            "ci_cd_files": [],
            "docker_files": [],
            "security_findings": []
        }

    def _is_test_file(self, filename: str, path_parts: List[str]) -> bool:
        """Determines if a file is likely a test based on name or location."""
        # Check path for 'test' folders
        if any(part.lower() in self.TEST_INDICATORS for part in path_parts):
            return True
        # Check filename conventions (e.g., .test.js, _spec.rb, test_*.py)
        lower_name = filename.lower()
        return (
            lower_name.endswith(('.test.js', '.test.ts', '.spec.js', '.spec.ts')) or
            lower_name.startswith('test_') or 
            lower_name.endswith('_test.py')
        )

    def _scan_content_for_secrets(self, file_path: str):
        """Quickly scans first 10KB of text files for obvious secrets."""
        try:
            # Only scan small text files
            if os.path.getsize(file_path) > 1024 * 50: 
                return

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for label, pattern in self.SECRET_PATTERNS.items():
                if pattern.search(content):
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    self.stats["security_findings"].append({
                        "type": label,
                        "file": rel_path
                    })
        except Exception:
            pass

    def scan(self) -> Dict[str, Any]:
        """
        Main execution method.
        """
        for root, dirs, files in os.walk(self.root_dir):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            # Calculate Depth
            rel_dir = os.path.relpath(root, self.root_dir)
            current_depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
            self.stats["depth"] = max(self.stats["depth"], current_depth)
            self.stats["dir_count"] += len(dirs)

            path_parts = rel_dir.split(os.sep)

            for file in files:
                file_path = os.path.join(root, file)
                self.stats["file_count"] += 1
                self.stats["total_size_kb"] += os.path.getsize(file_path) / 1024
                
                # Extension tally
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    self.stats["extensions"][ext] += 1
                
                # Categorization
                lower_file = file.lower()
                rel_path = os.path.join(rel_dir, file) if rel_dir != "." else file

                if lower_file in self.CONFIG_FILES:
                    self.stats["config_files"].append(rel_path)
                
                if "docker" in lower_file:
                    self.stats["docker_files"].append(rel_path)
                    
                if lower_file in ['.gitlab-ci.yml', '.travis.yml', 'circle.yml', 'jenkinsfile'] or '.github/workflows' in rel_path:
                    self.stats["ci_cd_files"].append(rel_path)

                if self._is_test_file(file, path_parts):
                    self.stats["test_files"].append(rel_path)

                # Security Scan (Lightweight)
                if ext in {'.py', '.js', '.ts', '.json', '.env', '.yml', '.xml', '.properties'}:
                    self._scan_content_for_secrets(file_path)

        return self._compute_metrics()

    def _compute_metrics(self) -> Dict[str, Any]:
        """Finalizes data and computes ratios."""
        code_files_count = sum(self.stats["extensions"].get(ext, 0) for ext in {'.py', '.js', '.ts', '.go', '.rb', '.java', '.c', '.cpp', '.php'})
        config_count = len(self.stats["config_files"])
        test_count = len(self.stats["test_files"])
        
        # Avoid division by zero
        code_config_ratio = round(code_files_count / config_count, 2) if config_count > 0 else 0
        test_code_ratio = round(test_count / code_files_count, 2) if code_files_count > 0 else 0

        return {
            "summary": {
                "total_files": self.stats["file_count"],
                "total_dirs": self.stats["dir_count"],
                "max_depth": self.stats["depth"],
                "size_kb": round(self.stats["total_size_kb"], 2)
            },
            "tech_signals": {
                "extensions": dict(self.stats["extensions"]),
                "configs": self.stats["config_files"],
                "docker": self.stats["docker_files"],
                "ci_cd": self.stats["ci_cd_files"]
            },
            "quality_metrics": {
                "test_files_count": test_count,
                "code_files_count": code_files_count,
                "code_to_config_ratio": code_config_ratio,
                "test_to_code_ratio": test_code_ratio
            },
            "security_scan": {
                "found_secrets": self.stats["security_findings"],
                "has_secrets": len(self.stats["security_findings"]) > 0
            }
        }