# Repository Analyzer - Complete Documentation

## 📋 System Overview

This is a **fact-grounded, multi-stage repository analysis system** that combines deterministic scanning, AI reasoning, and tool-based static analysis to provide comprehensive code quality insights.

### Three-Stage Architecture

```
Stage 1: PRE-SCAN (prescan.py)
   ↓ Deterministic file/config measurement
Stage 2: AI PRE-ANALYSIS (main.py + Gemini)
   ↓ Infers language, framework, app type
Stage 3: STATIC ANALYSIS (static_analysis/)
   ↓ Tool-based validation (Ruff, ESLint, etc.)
Final Output: Unified JSON Report
```

---

## 🗂️ Project Structure

```
project_root/
├── main.py                          # FastAPI orchestrator
├── prescan.py                       # Deterministic scanner
├── requirements.txt                 # Python dependencies
├── .env                             # GEMINI_API_KEY
│
└── static_analysis/                 # Static analysis engine
    ├── __init__.py
    ├── base.py                      # Abstract analyzer contract
    ├── python.py                    # Python toolchain
    ├── javascript.py                # JS/TS toolchain
    ├── runner.py                    # Orchestrator/router
    │
    ├── parsers/                     # Tool output parsers
    │   ├── __init__.py
    │   ├── ruff.py                  # Python linter
    │   ├── bandit.py                # Python security
    │   ├── radon.py                 # Python complexity
    │   ├── vulture.py               # Python dead code
    │   ├── eslint.py                # JS/TS linter
    │   ├── sonarjs.py               # JS/TS bug patterns
    │   └── semgrep.py               # Universal security
    │
    └── schemas/                     # JSON Schema validation
        ├── python.json
        └── js.json
```

---

## 🔧 Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

**Installed tools:**
- `ruff` - Fast Python linter
- `bandit` - Python security scanner
- `radon` - Complexity metrics
- `vulture` - Dead code detector
- `semgrep` - Universal security rules
- FastAPI, GitPython, google-generativeai

### 2. JavaScript/TypeScript Tools

```bash
# Global installation (recommended)
npm install -g eslint eslint-plugin-sonarjs

# Verify installation
eslint --version
```

### 3. Environment Setup

Create `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 How It Works

### **Stage 1: Pre-Scan** (`prescan.py`)

**Purpose:** Deterministic measurement without AI inference.

**What it does:**
- Counts files by extension (`.py`, `.js`, `.ts`, etc.)
- Identifies config files (`package.json`, `requirements.txt`, etc.)
- Detects Docker/CI-CD files
- Scans for hardcoded secrets (API keys, private keys)
- Calculates metrics (code-to-config ratio, test coverage)

**Output:**
```json
{
  "summary": {
    "total_files": 45,
    "total_dirs": 12,
    "max_depth": 4,
    "size_kb": 230.5
  },
  "tech_signals": {
    "extensions": {".py": 20, ".js": 15},
    "configs": ["package.json", "requirements.txt"],
    "docker": ["Dockerfile"],
    "ci_cd": [".github/workflows/ci.yml"]
  },
  "quality_metrics": {
    "test_files_count": 8,
    "code_to_config_ratio": 10.0,
    "test_to_code_ratio": 0.4
  },
  "security_scan": {
    "found_secrets": [],
    "has_secrets": false
  }
}
```

---

### **Stage 2: AI Pre-Analysis** (`main.py`)

**Purpose:** High-level reasoning about project structure.

**What it does:**
- Uses pre-scan data as **factual baseline**
- Reads critical files (`package.json`, `README.md`)
- Infers: language, runtime, framework, app type
- Identifies entry points and start instructions
- Provides evidence from actual files (no hallucinations)

**Output:**
```json
{
  "language": "JavaScript",
  "runtime": "Node.js",
  "framework": "Express",
  "app_type": "Backend API",
  "entry_point": "src/index.js",
  "start_instruction": "npm start",
  "framework_evidence": [
    {
      "source": "package.json",
      "signal": "dependency",
      "value": "express"
    }
  ],
  "confidence": 0.85,
  "ambiguities": [],
  "errors": []
}
```

---

### **Stage 3: Static Analysis** (`static_analysis/`)

**Purpose:** Tool-based validation and measurement.

**Routing Logic:**
```python
if ai_pre_analysis.language == "Python":
    → PythonAnalyzer
    → Tools: Ruff, Bandit, Radon, Vulture

elif ai_pre_analysis.language in ["JavaScript", "TypeScript"]:
    → JavaScriptAnalyzer
    → Tools: ESLint, SonarJS, Semgrep

elif ai_pre_analysis.app_type == "Full Stack":
    → Detect frontend/backend folders
    → Run both analyzers
    → Merge results
```

**Tool Responsibilities:**

| Language | Tool | Purpose | Output |
|----------|------|---------|--------|
| Python | Ruff | Linting, style | Errors, warnings, top rules |
| Python | Bandit | Security | Vulnerabilities by severity |
| Python | Radon | Complexity | Avg/max complexity, high-complexity functions |
| Python | Vulture | Dead code | Unused code count |
| JS/TS | ESLint | Linting, style | Errors, warnings, complexity violations |
| JS/TS | SonarJS | Bug patterns | Bugs, code smells |
| Universal | Semgrep | Security | Security issues by severity |

**Universal Output Schema:**
```json
{
  "language": "Python",
  "toolchain": ["ruff", "bandit", "radon", "vulture"],
  "results": {
    "syntax": {
      "errors": 3,
      "files_affected": 2
    },
    "style": {
      "warnings": 12,
      "top_violations": ["F401", "E501", "W503"]
    },
    "bugs": {
      "potential_bugs": 0,
      "dead_code": 5
    },
    "security": {
      "vulnerabilities": 2,
      "high_severity": 1,
      "severity_breakdown": {"HIGH": 1, "MEDIUM": 1, "LOW": 0}
    },
    "complexity": {
      "average": 6.2,
      "high_complexity_functions": 3,
      "max_complexity": 15
    }
  },
  "tool_status": {
    "ruff": "ok",
    "bandit": "ok",
    "radon": "ok",
    "vulture": "ok"
  },
  "errors": []
}
```

---

## 📊 Final API Response

**Endpoint:** `POST /analyze-repo`

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo"
}
```

**Response:**
```json
{
  "pre_scan": { /* Stage 1 output */ },
  "ai_pre_analysis": { /* Stage 2 output */ },
  "static_analysis": { /* Stage 3 output */ }
}
```

---

## 🔄 Data Flow Between Stages

```
1. prescan.py
   ↓ Outputs: file counts, extensions, configs
   
2. main.py (Gemini AI)
   ↓ Inputs: pre_scan results + file contents
   ↓ Outputs: language, framework, app_type
   
3. static_analysis/runner.py
   ↓ Inputs: pre_scan + ai_pre_analysis
   ↓ Routes to: PythonAnalyzer OR JavaScriptAnalyzer
   ↓ Outputs: Universal schema
   
4. main.py (FastAPI)
   ↓ Merges all three stages
   ↓ Returns: Final JSON
```

**Key Design Principle:**
> Each stage is **independent** but **informed** by the previous stage. Pre-scan provides facts, AI provides context, static analysis provides validation.

---

## 🛠️ Usage Examples

### Run Locally

```bash
# Start the server
python main.py

# In another terminal
curl -X POST http://localhost:8000/analyze-repo \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

### Programmatic Usage

```python
from static_analysis.runner import run_static_analysis
from prescan import PreScanner

# Stage 1
scanner = PreScanner("/path/to/repo")
pre_scan = scanner.scan()

# Stage 2 (simplified - normally done via Gemini)
ai_analysis = {
    "language": "Python",
    "app_type": "Backend API"
}

# Stage 3
static_result = run_static_analysis(
    repo_path="/path/to/repo",
    pre_scan=pre_scan,
    ai_pre_analysis=ai_analysis
)
```

---

## 🧪 Tool Installation Verification

```bash
# Python tools
ruff --version        # Should show v0.1.7+
bandit --version      # Should show v1.7.5+
radon --version       # Should show v6.0.1+
vulture --version     # Should show v2.10+
semgrep --version     # Should show v1.45.0+

# JavaScript tools
eslint --version      # Should show v8.0.0+
npm list -g eslint-plugin-sonarjs  # Should be installed
```

---

## ⚠️ Error Handling

### Tool Failures Never Block Pipeline

If a tool fails:
```json
{
  "tool_status": {
    "ruff": "ok",
    "bandit": "failed",  // ← Tool failed
    "radon": "ok",
    "vulture": "ok"
  },
  "errors": []  // Pipeline continues
}
```

**Failure reasons:**
- `"not installed"` - Binary not found in PATH
- `"timeout"` - Exceeded 60-180s limit
- `"invalid JSON output"` - Tool returned malformed data
- `"config missing"` - Auto-generation attempted

---

## 🎯 Full-Stack Project Handling

When `ai_pre_analysis.app_type` contains "Full Stack":

**Detection Logic:**
1. Frontend: Searches for `client/`, `frontend/`, `web/`, `app/` with JS/TS files
2. Backend: Searches for `server/`, `backend/`, `api/` or defaults to root

**Output:**
```json
{
  "project_type": "full-stack",
  "frontend_analysis": {
    "language": "JavaScript",
    "toolchain": ["eslint", "sonarjs", "semgrep"],
    "results": { /* JS analysis */ }
  },
  "backend_analysis": {
    "language": "Python",
    "toolchain": ["ruff", "bandit", "radon", "vulture"],
    "results": { /* Python analysis */ }
  },
  "errors": []
}
```

---

## 📐 Architecture Principles

1. **Separation of Concerns**
   - Pre-scan: Measures
   - AI: Reasons
   - Static: Validates

2. **Never Guess, Always Measure**
   - No AI hallucinations (uses pre-scan as ground truth)
   - No dummy data (all parsers functional)
   - No interpretation (tools report facts)

3. **Fail-Safe Design**
   - Tools can fail individually
   - Pipeline always completes
   - Errors are reported, not raised

4. **Universal Schema**
   - Same output structure across all languages
   - Scoring layer (future) doesn't care which tools ran

---

## 🔮 Next Steps (Future Enhancements)

- **Scoring Layer**: Convert static analysis results into quality scores
- **Runtime Analysis**: Execute tests, measure coverage
- **Additional Languages**: Go, Rust, Java support
- **Custom Rules**: User-defined quality thresholds
- **CI/CD Integration**: GitHub Actions, GitLab CI hooks

---

## 📝 File Descriptions

### Core Files

- **main.py**: FastAPI server, orchestrates all 3 stages, clones repos
- **prescan.py**: Deterministic scanner, no AI, pure measurement
- **requirements.txt**: All Python dependencies

### Static Analysis Module

- **base.py**: Abstract `StaticAnalyzer` class (contract for all analyzers)
- **python.py**: Implements Python toolchain, calls parsers
- **javascript.py**: Implements JS/TS toolchain, auto-generates configs
- **runner.py**: Routes to correct analyzer based on language/app_type

### Parsers (Tool Output → Structured Dict)

- **ruff.py**: Parses Ruff JSON → errors, warnings, top rules
- **bandit.py**: Parses Bandit JSON → vulnerabilities by severity
- **radon.py**: Parses Radon JSON → complexity metrics
- **vulture.py**: Parses Vulture lines → dead code count
- **eslint.py**: Parses ESLint JSON → errors, warnings, complexity
- **sonarjs.py**: Parses SonarJS/ESLint → bugs, code smells
- **semgrep.py**: Parses Semgrep JSON → security issues

### Schemas (Validation)

- **python.json**: JSON Schema for Python analysis output
- **js.json**: JSON Schema for JS/TS analysis output

---

## 🤝 Contributing

To add a new language:

1. Create `static_analysis/your_language.py` extending `StaticAnalyzer`
2. Create parsers in `static_analysis/parsers/`
3. Register in `runner.py`'s `_select_analyzer()` method
4. Create schema in `static_analysis/schemas/your_language.json`

---

## 📄 License

This project separates deterministic measurement from AI reasoning to ensure credibility and reproducibility.

**Philosophy:** *Facts first, reasoning second, judgment third.*