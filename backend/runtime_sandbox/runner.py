"""
runtime_sandbox/runner.py
High-Class Edition: Adds Severity Scoring & Intelligent Classification
"""
import docker
import logging
import time
import re
from docker.errors import BuildError
import os

logger = logging.getLogger(__name__)

# SECURITY & LIMITS
LIMIT_CPU = 0.5
LIMIT_RAM = "512m"
LIMIT_TIMEOUT = 60  # 60s Execution Limit

# EXPANDED MOCK ENV
SAFE_MOCK_ENV = {
    "NODE_ENV": "development",
    "PORT": "3000",
    "DEBUG": "true",
    "FLASK_ENV": "development",
    "FLASK_DEBUG": "1",
    "PYTHONUNBUFFERED": "1",
    "MONGO_URI": "mongodb://mock-mongo:27017/testdb",
    "MONGODB_URI": "mongodb://mock-mongo:27017/testdb",
    "DATABASE_URL": "postgres://user:pass@localhost:5432/db",
    "API_KEY": "mock-api-key-123",
    "SECRET_KEY": "mock-secret-key-safe",
    "JWT_SECRET": "mock-jwt-secret"
}

class LogAnalyzer:
    """Parses raw logs for structured insights."""
    
    ERROR_PATTERNS = [
        (r"MongooseError", "Database Connection Fail"),
        (r"ModuleNotFoundError", "Missing Python Dependency"),
        (r"ImportError", "Import Error"),
        (r"SyntaxError", "Syntax Error"),
        (r"ReferenceError", "Code Reference Error"),
        (r"TypeError", "Type Mismatch"),
        (r"Traceback \(most recent call last\)", "Python Crash Trace"),
        (r"Error: Cannot find module", "Missing Node Module"),
        (r"unhandledRejection", "Unhandled Promise Rejection"),
        (r"Address already in use", "Port Conflict"),
        (r"CRITICAL:", "Critical Log Level"),
        (r"Exception:", "Generic Exception"),
        (r"Error:", "Generic Error")
    ]

    PORT_PATTERNS = [
        r"Running on http://.*:(\d+)",
        r"Listening on port (\d+)",
        r"started on port (\d+)",
        r"server listening on (\d+)",
        r":(\d+) \.\.\.",
        r"localhost:(\d+)",
        r"0\.0\.0\.0:(\d+)"
    ]

    @staticmethod
    def analyze(log_str: str) -> dict:
        results = {"errors": [], "detected_port": None}
        
        for pattern, label in LogAnalyzer.ERROR_PATTERNS:
            if re.search(pattern, log_str, re.IGNORECASE):
                matches = re.findall(pattern + r".*", log_str, re.IGNORECASE)
                detail = matches[0] if matches else label
                results["errors"].append(f"[{label}] {detail.strip()[:150]}")

        for pattern in LogAnalyzer.PORT_PATTERNS:
            match = re.search(pattern, log_str)
            if match:
                results["detected_port"] = int(match.group(1))
                break
                
        return results

def run_runtime_sandbox(repo_path: str, ai_context: dict) -> dict:
    if os.name == "nt":
        os.environ["DOCKER_HOST"] = "npipe:////./pipe/docker_engine"
    
    # 5-minute timeout for slow Windows Docker
    try:
        client = docker.from_env(timeout=300)
    except Exception as e:
        return {
            "classification": "system_error",
            "health": {"severity": "critical"},
            "errors": [f"Docker Client Init Failed: {str(e)}"]
        }

    image_tag = f"repo-analysis-{int(time.time())}"
    
    result = {
        "docker": {"image_built": False, "build_time_ms": 0, "build_errors": []},
        "execution": {"status": "pending", "exit_code": None, "logs": {"stdout": "", "stderr": ""}},
        "health": {
            "process_alive": False, 
            "port_opened": False, 
            "detected_app_port": None, 
            "docker_exposed_ports": [],
            "port_mismatch": False,
            "severity": "unknown" # <--- NEW FIELD
        },
        "classification": "unknown",
        "errors": [],
        "env_injected": list(SAFE_MOCK_ENV.keys())
    }

    # 1. BUILD
    start_build = time.time()
    try:
        logger.info(f"Building {image_tag}...")
        image, _ = client.images.build(path=repo_path, tag=image_tag, rm=True, forcerm=True)
        result["docker"]["image_built"] = True
        result["docker"]["build_time_ms"] = int((time.time() - start_build) * 1000)
    except BuildError as e:
        result["docker"]["build_errors"].append(str(e))
        result["classification"] = "build_failure"
        result["health"]["severity"] = "critical"
        result["errors"].append("Docker build failed")
        return result
    except Exception as e:
        result["errors"].append(f"Docker system error: {str(e)}")
        result["health"]["severity"] = "critical"
        return result

    # 2. RUN
    container = None
    try:
        logger.info(f"Running {image_tag}...")
        start_run = time.time()
        
        container = client.containers.run(
            image_tag,
            detach=True,
            mem_limit=LIMIT_RAM,
            nano_cpus=int(LIMIT_CPU * 1000000000),
            publish_all_ports=True, 
            environment=SAFE_MOCK_ENV
        )
        
        time.sleep(8) 
        container.reload()
        state = container.attrs['State']
        result["execution"]["status"] = state['Status']
        result["execution"]["exit_code"] = state['ExitCode']
        result["execution"]["startup_time_ms"] = int((time.time() - start_run) * 1000)

        # 3. LOG ANALYSIS
        raw_logs = container.logs(stdout=True, stderr=True).decode('utf-8', errors='replace')
        result["execution"]["logs"]["stdout"] = raw_logs[:15000]
        
        analysis = LogAnalyzer.analyze(raw_logs)
        detected_errors = analysis["errors"]
        detected_port = analysis["detected_port"]
        result["health"]["detected_app_port"] = detected_port
        
        # 4. HEALTH CHECKS
        is_running = state['Running']
        result["health"]["process_alive"] = is_running
        
        ports_dict = container.attrs['NetworkSettings']['Ports']
        exposed_ports = [int(p.split('/')[0]) for p in ports_dict.keys()] if ports_dict else []
        result["health"]["docker_exposed_ports"] = exposed_ports
        result["health"]["port_opened"] = len(exposed_ports) > 0

        # Port Mismatch
        if detected_port and exposed_ports:
            if detected_port not in exposed_ports:
                result["health"]["port_mismatch"] = True
                result["errors"].append(f"Port Mismatch: App listens on {detected_port}, but Dockerfile exposes {exposed_ports}")

        # 5. CLASSIFICATION & SEVERITY SCORING
        if state['ExitCode'] != 0 and state['ExitCode'] is not None:
            result["classification"] = "crashed_on_start"
            result["health"]["severity"] = "critical"
            result["errors"].append(f"Exit Code {state['ExitCode']}")
            result["errors"].extend(detected_errors)

        elif detected_errors:
            result["classification"] = "unhealthy_runtime_errors"
            result["health"]["severity"] = "critical"
            result["errors"].extend(detected_errors)
            
        elif is_running:
             if detected_port:
                 if result["health"]["port_mismatch"]:
                     result["classification"] = "running_port_mismatch"
                     result["health"]["severity"] = "warning"
                 else:
                     result["classification"] = "healthy_verified_port"
                     result["health"]["severity"] = "ok"
             elif exposed_ports:
                 result["classification"] = "running_blind_ports"
                 result["health"]["severity"] = "warning"
             else:
                 result["classification"] = "running_no_port_detected"
                 result["health"]["severity"] = "warning"
        else:
            result["classification"] = "exited_cleanly"
            result["health"]["severity"] = "ok"

    except Exception as e:
        result["execution"]["status"] = "system_error"
        result["health"]["severity"] = "critical"
        result["errors"].append(str(e))
    finally:
        if container:
            try:
                container.stop(timeout=1); container.remove()
            except Exception: pass
        try:
            client.images.remove(image_tag, force=True)
        except Exception: pass

    return result