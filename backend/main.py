"""
main.py

FastAPI orchestrator with Elite Correlation & Noise Suppression.
"""
import os
import shutil
import uuid
import logging
import stat
import errno
import git
import warnings
import sys

# --- SILENCE WARNINGS (MUST BE BEFORE IMPORTS) ---
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
warnings.filterwarnings("ignore", category=FutureWarning)
try:
    # Silence the specific Google GenAI warning
    warnings.filterwarnings("ignore", module="google.generativeai")
except:
    pass
# -------------------------------------------------

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from prescan import PreScanner
from static_analysis.runner import run_static_analysis
from ai_pre_analysis import analyze_with_gemini

# Bridge to Runtime
try:
    from runtime_sandbox import run_runtime_analysis
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEMP_DIR_BASE = "./temp_repos"

app = FastAPI(title="Repo Analyzer (Elite Edition)")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

genai.configure(api_key=GEMINI_API_KEY)


class RepoRequest(BaseModel):
    repo_url: str

def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

def cleanup_repo(path: str):
    try:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)
            logger.info(f"Cleaned up {path}")
    except Exception as e:
        logger.error(f"Error cleaning up {path}: {e}")

def get_file_structure(root_dir: str) -> str:
    file_tree = []
    ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode', 'dist', 'build', '.next'}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        file_tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for i, f in enumerate(files):
            if i > 25: 
                file_tree.append(f"{subindent}... (more files)")
                break
            file_tree.append(f"{subindent}{f}")
    return "\n".join(file_tree)

def read_critical_files(root_dir: str) -> str:
    critical_files = [
        "package.json", "requirements.txt", "pyproject.toml", 
        "Dockerfile", "docker-compose.yml", "procfile", "Makefile"
    ]
    content_buffer = []
    for file in os.listdir(root_dir):
        if file.lower() in [f.lower() for f in critical_files] or file.lower().startswith("readme"):
            file_path = os.path.join(root_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()[:2000]
                    content_buffer.append(f"\n--- CONTENT OF {file} ---\n{file_content}\n")
            except Exception: pass
    return "\n".join(content_buffer)

# --- ELITE CORRELATION LOGIC ---
def correlate_insights(prescan, ai, static, runtime):
    """
    Cross-references stages to find hidden issues.
    """
    insights = []
    
    # 1. Config Mismatches
    if runtime.get("health", {}).get("port_mismatch"):
        insights.append({
            "type": "config_error",
            "severity": "high",
            "message": f"Port Mismatch: App listens on {runtime['health']['detected_app_port']}, but Docker exposes {runtime['health']['docker_exposed_ports']}."
        })

    # 2. Environment Variable Crashes
    runtime_errors = str(runtime.get("errors", [])).lower()
    if "env" in runtime_errors or "key" in runtime_errors or "mongo" in runtime_errors:
        insights.append({
            "type": "missing_config",
            "severity": "critical",
            "message": "Runtime crashed likely due to missing Environment Variables (DB or Keys). Mock injection failed to satisfy app."
        })

    # 3. Static vs Runtime
    if static.get("tool_status", {}).get("eslint") == "failed":
        insights.append({
            "type": "tooling_gap",
            "severity": "medium",
            "message": "Static Analysis incomplete (ESLint failed). Code quality score is unreliable."
        })
        
    return insights
# ------------------------------------

@app.post("/analyze-repo")
async def analyze_repo(request: RepoRequest, background_tasks: BackgroundTasks):
    folder_name = f"repo_{uuid.uuid4().hex}"
    repo_path = os.path.join(TEMP_DIR_BASE, folder_name)

    try:
        if not os.path.exists(TEMP_DIR_BASE):
            os.makedirs(TEMP_DIR_BASE)
        git.Repo.clone_from(request.repo_url, repo_path)
        
        # STAGE 1
        scanner = PreScanner(repo_path)
        prescan_result = scanner.scan()

        # STAGE 2
        structure = get_file_structure(repo_path)
        critical_content = read_critical_files(repo_path)
        ai_result = await analyze_with_gemini(structure, critical_content, prescan_result)
        
        # STAGE 3
        static_result = run_static_analysis(repo_path, prescan_result, ai_result)

        # STAGE 4
        runtime_result = {"status": "skipped"}
        if RUNTIME_AVAILABLE:
            try:
                runtime_context = ai_result.copy()
                runtime_context['prescan'] = prescan_result
                runtime_result = run_runtime_analysis(repo_path, runtime_context)
            except Exception as e:
                logger.error(f"Runtime failed: {e}")
                runtime_result = {"status": "error", "error": str(e), "health": {"severity": "critical"}}
        
        # STAGE 5: CORRELATION
        insights = correlate_insights(prescan_result, ai_result, static_result, runtime_result)

        background_tasks.add_task(cleanup_repo, repo_path)
        
        return {
            "pre_scan": prescan_result,
            "ai_pre_analysis": ai_result,
            "static_analysis": static_result,
            "runtime_analysis": runtime_result,
            "insights": insights 
        }

    except Exception as e:
        cleanup_repo(repo_path)
        return {"error": "System Error", "details": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "repo-analyzer"}


if __name__ == "__main__":
    import uvicorn
    # Clean logs for production feel
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")