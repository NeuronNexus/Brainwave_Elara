"""
static_analysis/parsers/__init__.py

Parser module for static analysis tools
"""
from static_analysis.parsers.ruff import parse_ruff_output
from static_analysis.parsers.bandit import parse_bandit_output
from static_analysis.parsers.radon import parse_radon_output
from static_analysis.parsers.vulture import parse_vulture_output
from static_analysis.parsers.eslint import parse_eslint_output
from static_analysis.parsers.sonarjs import parse_sonarjs_output
from static_analysis.parsers.semgrep import parse_semgrep_output

__all__ = [
    'parse_ruff_output',
    'parse_bandit_output',
    'parse_radon_output',
    'parse_vulture_output',
    'parse_eslint_output',
    'parse_sonarjs_output',
    'parse_semgrep_output'
]