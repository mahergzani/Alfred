# main.py
# This script orchestrates a team of AI agents for a security audit workflow.

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List
import json

# --- Configuration ---
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    if not api_key:
        raise KeyError
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")
except KeyError:
    print("ERROR: GOOGLE_API_KEY not found or is empty in your .env file.")
    exit()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Security Audit Agent API",
    description="Provides endpoints for the different AI agents in the security audit workflow.",
)

# --- CORS Configuration ---
origins = [
    "https://mahergzani.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Manual OPTIONS Route Handlers (The Final Fix) ---
# These will catch the browser's "preflight" requests and respond with permission.

@app.options("/create-tactical-plan")
async def options_create_tactical_plan():
    return Response(status_code=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})

@app.options("/run-pentest")
async def options_run_pentest():
    return Response(status_code=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})

@app.options("/triage-findings")
async def options_triage_findings():
    return Response(status_code=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})

@app.options("/fix-vulnerability")
async def options_fix_vulnerability():
    return Response(status_code=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})


# --- Agent 1: Security Manager ---

class StrategicGoalRequest(BaseModel):
    repo_url: str
    strategic_goal: str

class TacticalPlanResponse(BaseModel):
    tactical_plan: str

SECURITY_MANAGER_PROMPT = """
You are an expert AI Security Manager. Your role is to translate high-level business goals into specific, actionable technical plans for your team of penetration testers. A user will provide you with a GitHub repository URL and a strategic goal. Your task is to generate a concise tactical plan for a white-box security assessment. The plan MUST be actionable, specific, scoped, and formatted as a single string.
"""

@app.post("/create-tactical-plan", response_model=TacticalPlanResponse)
async def create_tactical_plan(request: StrategicGoalRequest):
    print(f"Received strategic goal: '{request.strategic_goal}' for repo: {request.repo_url}")
    model = genai.GenerativeModel(model_name='gemini-2.5-flash-preview-05-20', system_instruction=SECURITY_MANAGER_PROMPT)
    user_input = f"Strategic Goal: \"{request.strategic_goal}\"\nRepo URL: \"{request.repo_url}\""
    response = model.generate_content(user_input)
    tactical_plan = response.text.strip()
    print(f"Generated Tactical Plan: {tactical_plan}")
    return TacticalPlanResponse(tactical_plan=tactical_plan)

# --- Agent 2: Penetration Tester ---

class VulnerabilityFinding(BaseModel):
    file_path: str = Field(description="The path to the vulnerable file in the repository.")
    line_number: int = Field(description="The specific line number where the vulnerability occurs.")
    vulnerability_type: str = Field(description="The class of vulnerability (e.g., 'SQL Injection', 'Hardcoded Secret').")
    description: str = Field(description="A brief explanation of the vulnerability and its potential impact.")
    remediation: str = Field(description="A clear suggestion on how to fix the vulnerability.")

class PenTestRequest(BaseModel):
    repo_url: str
    tactical_plan: str
    code_content_for_review: str

class PenTestResponse(BaseModel):
    findings: List[VulnerabilityFinding]

PENETRATION_TESTER_PROMPT = """
You are an expert AI Penetration Tester. Your role is to perform a white-box security assessment based on a given tactical plan and source code. You will be provided with a tactical plan and a snippet of source code. Your task is to analyze the code and identify all security vulnerabilities. You MUST return your findings as a valid JSON object with a single key "findings" which contains an array of vulnerability objects. Each object must contain: 'file_path', 'line_number', 'vulnerability_type', 'description', and 'remediation'. If you find no vulnerabilities, return `{"findings": []}`.
"""

@app.post("/run-pentest", response_model=PenTestResponse)
async def run_pentest(request: PenTestRequest):
    print(f"Received pentest request for repo: {request.repo_url}")
    response_data = None
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-preview-05-20',
            system_instruction=PENETRATION_TESTER_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
        user_input = f'Tactical Plan: "{request.tactical_plan}"\n\nSource Code to Analyze:\n---\n{request.code_content_for_review}\n---'
        response = model.generate_content(user_input)
        if not response.parts:
             raise HTTPException(status_code=400, detail=f"The model blocked the request due to safety settings.")
        response_data = response.text
        if isinstance(response_data, dict):
            return PenTestResponse.model_validate(response_data)
        elif isinstance(response_data, str):
            raw_text = response_data.strip().replace("```json", "").replace("```", "").strip()
            return PenTestResponse.model_validate_json(raw_text)
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected response type from AI model: {type(response_data)}")
    except (ValidationError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"The AI agent returned a response that was not valid JSON. Raw response: {response_data}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. Raw AI Response: {response_data}. Error: {e}")

# --- Agent 3: Security Engineer ---

class ActionSummary(BaseModel):
    action_taken: str
    details: str

class TriageRequest(BaseModel):
    repo_url: str
    findings: List[VulnerabilityFinding]
    github_token: str = Field(description="A GitHub Personal Access Token to authorize creating issues.")

class TriageResponse(BaseModel):
    summary: List[ActionSummary]

@app.post("/triage-findings", response_model=TriageResponse)
async def triage_findings(request: TriageRequest):
    print(f"Received triage request for {len(request.findings)} findings in repo: {request.repo_url}")
    actions = []
    for i, finding in enumerate(request.findings):
        issue_title = f"Security Vulnerability: {finding.vulnerability_type} in {finding.file_path}"
        actions.append(ActionSummary(action_taken="Simulated GitHub Issue Creation", details=f"Created Issue #{i+1}: '{issue_title}' for the development team."))
    return TriageResponse(summary=actions)

# --- Agent 4: Software Engineer ---

class FixRequest(BaseModel):
    vulnerability_finding: VulnerabilityFinding
    vulnerable_code: str

class FixResponse(BaseModel):
    fixed_code: str
    commit_message: str

SOFTWARE_ENGINEER_PROMPT = """
You are an expert AI Software Engineer specializing in security. Your task is to fix a security vulnerability in a given snippet of code. You will be provided with a detailed vulnerability report and the exact block of vulnerable source code. Your job is to rewrite the code to fix the vulnerability according to the best security practices. You MUST return a JSON object with two keys: `fixed_code` and `commit_message`.
"""

@app.post("/fix-vulnerability", response_model=FixResponse)
async def fix_vulnerability(request: FixRequest):
    print(f"Received fix request for vulnerability: {request.vulnerability_finding.vulnerability_type}")
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-preview-05-20',
            system_instruction=SOFTWARE_ENGINEER_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
        finding_json = request.vulnerability_finding.model_dump_json(indent=2)
        user_input = f"Vulnerability Report:\n{finding_json}\n\nVulnerable Code:\n---\n{request.vulnerable_code}\n---"
        response = model.generate_content(user_input)
        return FixResponse.model_validate_json(response.text)
    except (ValidationError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"The AI agent returned a malformed JSON response for the code fix.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while generating the code fix.")

# This allows the script to be run directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

