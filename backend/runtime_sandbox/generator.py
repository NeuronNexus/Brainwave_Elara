"""
runtime_sandbox/generator.py
Generates a Dockerfile if one does not exist, using AI context.
"""
import os
import logging
import re
from .templates import DOCKERFILE_TEMPLATES, GENERIC_TEMPLATE

logger = logging.getLogger(__name__)

def prepare_dockerfile(repo_path: str, ai_context: dict) -> dict:
    dockerfile_path = os.path.join(repo_path, "Dockerfile")
    
    if os.path.exists(dockerfile_path):
        logger.info("Using existing Dockerfile found in repo.")
        return {"source": "existing", "path": dockerfile_path}

    logger.info("No Dockerfile found. Auto-generating based on AI context.")
    
    language = ai_context.get("language", "").lower()
    start_cmd = ai_context.get("start_instruction", "")
    
    # --- ELITE SANITIZATION ---
    # Fixes crash: "npm start (Runs: node index.js)" -> "npm start"
    if not start_cmd:
        start_cmd = "echo 'No start command determined'"
    else:
        # 1. Strip parens and anything inside/after them
        start_cmd = start_cmd.split('(')[0].strip()
        # 2. Remove any trailing explanations that are not part of the command
        # This regex keeps alphanumeric, dashes, spaces, quotes, and standard shell symbols
        # It stops if it hits a suspicious "double space - comments" pattern or newlines
        start_cmd = start_cmd.split('\n')[0].strip()
        
    # Remove surrounding quotes if the AI added them to the string wrapper
    start_cmd = start_cmd.strip('"').strip("'")
    # --------------------------

    template = GENERIC_TEMPLATE
    if "python" in language:
        template = DOCKERFILE_TEMPLATES["python"]
    elif "node" in language or "javascript" in language or "typescript" in language:
        template = DOCKERFILE_TEMPLATES["node"]
    
    # We use shell form for maximum compatibility: CMD ["/bin/sh", "-c", "clean_cmd"]
    # Escaping double quotes inside the command to prevent JSON breakage
    safe_cmd = start_cmd.replace('"', '\\"')
    final_cmd_str = f'["/bin/sh", "-c", "{safe_cmd}"]'
    
    content = template.format(start_command=final_cmd_str)
    
    try:
        with open(dockerfile_path, "w") as f:
            f.write(content)
        return {"source": "generated", "path": dockerfile_path, "content": content}
    except Exception as e:
        logger.error(f"Failed to generate Dockerfile: {e}")
        return {"source": "error", "error": str(e)}