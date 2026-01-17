import logging
import json
import google.generativeai as genai
from google.api_core import exceptions
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Fallback Models (Fastest -> Strongest)
MODEL_CANDIDATES = [
    "models/gemini-2.0-flash",       
    "models/gemini-flash-latest",    
    "models/gemini-1.5-flash",
    "models/gemini-pro",
]

# ------------------------------------------------------------------
# POST-PROCESSING (AI Output Normalization)
# ------------------------------------------------------------------
def enforce_constraints(data: dict) -> dict:
    """Enforce output constraints on AI response."""
    # 1. Cap Confidence
    if "confidence" in data:
        data["confidence"] = min(float(data["confidence"]), 0.9)
    else:
        data["confidence"] = 0.5
        
    # 2. Ensure Verification State Exists
    if "verification_state" not in data:
        data["verification_state"] = {"rules": False, "ai": True, "runtime": False}

    # 3. Ensure Arrays exist
    for list_field in ["ambiguities", "errors", "entry_point_candidates"]:
        if list_field not in data or not isinstance(data[list_field], list):
            data[list_field] = []

    return data


# ------------------------------------------------------------------
# STAGE 2: AI ANALYSIS
# ------------------------------------------------------------------
async def analyze_with_gemini(file_structure: str, file_contents: str, prescan_data: dict) -> Dict[str, Any]:
    """
    Stage 2: AI Pre-Analysis
    Uses pre-scan data as factual baseline, infers high-level concepts.
    """
    prescan_json = json.dumps(prescan_data, indent=2)

    prompt = f"""
    You are a Technical Code Auditor. 
    Analyze the repository using the provided PRE-SCAN DATA as the factual baseline.
    
    Output a STRICT JSON object. No markdown.
    
    --- INPUT CONTEXT ---
    1. FACTUAL DATA: Use the provided "Pre-Scan" JSON. Do not hallucinate files not listed there.
    2. VISUAL CONTEXT: Use the "File Tree" to understand hierarchy.
    3. CONTENT CONTEXT: Use "Critical File Contents" for frameworks/dependencies.

    --- RULES FOR OUTPUT ---
    1. "confidence": Max value 0.9.
    2. "evidence": Use objects: {{ "source": "filename", "signal": "dependency/script", "value": "string" }}.
    3. DO NOT output "metrics_analysis" or "security_notes". Stick to structural classification.
    
    --- REQUIRED JSON STRUCTURE (AI PRE-ANALYSIS) ---
    {{
      "language": "String (e.g. JavaScript)",
      "runtime": "String (e.g. Node.js)",
      "framework": "String (e.g. Express, Django, React)",
      "app_type": "String (e.g. Backend API, Frontend SPA, CLI Tool, Full Stack)",
      
      "verification_state": {{
        "rules": true,
        "ai": true,
        "runtime": false
      }},

      "entry_point": "String",
      "entry_point_candidates": ["String"],
      "start_instruction": "String",
      
      "framework_evidence": [
         {{ "source": "String", "signal": "String", "value": "String" }}
      ],
      
      "summary": "Brief functional summary of what the code DOES (not how good it is).",
      "ambiguities": ["String"],
      "confidence": Float,
      "errors": ["String"]
    }}

    --- DETERMINISTIC PRE-SCAN DATA (FACTUAL BASELINE) ---
    {prescan_json}

    --- PROJECT FILE TREE ---
    {file_structure[:4000]} 

    --- CRITICAL FILE CONTENTS ---
    {file_contents}
    """

    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            logger.info(f"Attempting analysis with model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            content = response.text
            content = content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content)
            final_data = enforce_constraints(data)
            
            logger.info(f"Success with {model_name}!")
            return final_data
            
        except exceptions.ResourceExhausted:
            logger.warning(f"Quota exceeded for {model_name}. Switching...")
            last_error = "Quota Exceeded"
            continue 
        except json.JSONDecodeError:
            logger.warning(f"Model {model_name} returned invalid JSON. Switching...")
            last_error = "Invalid JSON"
            continue
        except Exception as e:
            logger.warning(f"Error with {model_name}: {e}")
            last_error = str(e)
            continue
    
    return {
        "language": "Unknown",
        "confidence": 0.0,
        "errors": [f"All AI models failed. Last error: {last_error}"],
        "ambiguities": [],
        "verification_state": {"rules": False, "ai": False, "runtime": False}
    }