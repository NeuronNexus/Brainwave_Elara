"""
runtime_sandbox/__init__.py
Exposes the main entry point for the Runtime Sandbox module.
"""
from .generator import prepare_dockerfile
from .runner import run_runtime_sandbox

def run_runtime_analysis(repo_path: str, ai_context: dict) -> dict:
    """
    Orchestrates the runtime analysis:
    1. Generates/Locates Dockerfile
    2. Builds and Runs container
    3. Merges results
    """
    # 1. Prepare Dockerfile (Generate if missing)
    prepare_result = prepare_dockerfile(repo_path, ai_context)
    
    # 2. Run Analysis (Build -> Run -> Log Parse)
    run_result = run_runtime_sandbox(repo_path, ai_context)
    
    # 3. Add context about the Dockerfile source
    run_result["dockerfile_source"] = prepare_result.get("source", "unknown")
    
    return run_result