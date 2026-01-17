"""
static_analysis/__init__.py

Static analysis module initialization
"""
from static_analysis.runner import run_static_analysis, StaticAnalysisRunner
from static_analysis.base import StaticAnalyzer, ToolResult
from static_analysis.python import PythonAnalyzer
from static_analysis.javascript import JavaScriptAnalyzer

__all__ = [
    'run_static_analysis',
    'StaticAnalysisRunner',
    'StaticAnalyzer',
    'ToolResult',
    'PythonAnalyzer',
    'JavaScriptAnalyzer'
]