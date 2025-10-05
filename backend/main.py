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
from typing import Optional
import json
import subprocess # To run git commands
import tempfile   # To create temporary directories
import shutil     # To clean up directories
import requests   # To interact with the GitHub API

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

# --- Manual OPTIONS Route Handlers ---
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(status_code=204, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, GET, OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})


# --- Helper Function ---
def get_repo_owner_and_name(repo_url):
    try:
        parts = repo_url.strip().rstrip('.git').split('/')
        return parts[-2], parts[-1]
    except IndexError:
        return None, None

# --- Agent 1: Security Manager ---
class StrategicGoalRequest(BaseModel):
    repo_url: str
    strategic_goal: str

class TacticalPlanResponse(BaseModel):
    tactical_plan: str

SECURITY_MANAGER_PROMPT = """You are an expert AI Security Manager...""" # Omitted for brevity

@app.post("/create-tactical-plan", response_model=TacticalPlanResponse)
async def create_tactical_plan(request: StrategicGoalRequest):
    print(f"Received strategic goal: '{request.strategic_goal}' for repo: {request.repo_url}")
    model = genai.GenerativeModel(model_name='gemini-2.5-flash-preview-05-20', system_instruction=SECURITY_MANAGER_PROMPT)
    user_input = f"Strategic Goal: \"{request.strategic_goal}\"\nRepo URL: \"{request.repo_url}\""
    response = model.generate_content(user_input)
    tactical_plan = response.text.strip()
    return TacticalPlanResponse(tactical_plan=tactical_plan)

# --- Agent 2: Penetration Tester ---

class VulnerabilityFinding(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    vulnerability_type: str
    description: str
    remediation: str


class PenTestRequest(BaseModel):
    repo_url: str
    tactical_plan: str

class PenTestResponse(BaseModel):
    findings: List[VulnerabilityFinding]

PENETRATION_TESTER_PROMPT = """
You are an expert AI Penetration Tester. Your task is to analyze the provided source code and tactical plan to identify security vulnerabilities.

Return your results strictly as a JSON object with exactly one key named "findings".
The value of "findings" must be a list of vulnerability objects, each containing details such as file_path, line_number, vulnerability_type, description, and remediation.
If you find no vulnerabilities, return { "findings": [] }.
Do not include any other text, keys, or explanations outside this JSON structure.
"""


@app.post("/run-pentest", response_model=PenTestResponse)
async def run_pentest(request: PenTestRequest):
    print(f"Received real pentest request for repo: {request.repo_url}")
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            subprocess.run(["git", "clone", request.repo_url, temp_dir], check=True, capture_output=True, text=True)
            code_content_for_review = ""
            file_count = 0
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file_count < 10 and file.endswith(('.py', '.js', '.html', 'Dockerfile', '.md', '.json', '.yaml', '.yml')):
                        try:
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, temp_dir)
                            code_content_for_review += f"\n--- START OF FILE: {relative_path} ---\n"
                            with open(file_path, 'r', encoding='utf-8') as f: code_content_for_review += f.read(10000)
                            code_content_for_review += f"\n--- END OF FILE: {relative_path} ---\n"
                            file_count += 1
                        except Exception: pass
            if not code_content_for_review: raise HTTPException(status_code=400, detail="No readable files found.")
            model = genai.GenerativeModel(model_name='gemini-2.5-flash-preview-05-20', system_instruction=PENETRATION_TESTER_PROMPT, generation_config={"response_mime_type": "application/json"})
            user_input = f'Tactical Plan: "{request.tactical_plan}"\n\nSource Code to Analyze:\n{code_content_for_review}'
            response = model.generate_content(user_input)
            raw_text = response.text
            print(f"--- RAW AI RESPONSE (Pentester) ---\n{raw_text}\n-----------------------")
            try:
                response_json = json.loads(raw_text)
                # If response is a list, wrap it under 'findings'
                if isinstance(response_json, list):
                    response_json = {"findings": response_json}
                # If response is a dict but doesn't have 'findings', look for likely candidates
                elif "findings" not in response_json:
                    # Try to find a key that contains a list of dicts with vulnerability info
                    for k, v in response_json.items():
                        if isinstance(v, list) and all(isinstance(item, dict) and "file_path" in item for item in v):
                            response_json = {"findings": v}
                            break
                    else:
                        raise HTTPException(status_code=500, detail=f"AI response is missing the 'findings' key. Raw: {raw_text}")
                return PenTestResponse.model_validate(response_json)
            except (json.JSONDecodeError, ValidationError) as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse or validate AI response: {e}. Raw: {raw_text}")
        except subprocess.CalledProcessError as e: raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e.stderr}")
        except Exception as e: raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# --- Agent 3: Security Engineer ---
class ActionSummary(BaseModel):
    action_taken: str; details: str; url: str
class TriageRequest(BaseModel):
    repo_url: str; findings: List[VulnerabilityFinding]; github_token: str
class TriageResponse(BaseModel):
    summary: List[ActionSummary]

@app.post("/triage-findings", response_model=TriageResponse)
async def triage_findings(request: TriageRequest):
    print(f"Received real triage request for {len(request.findings)} findings.")
    owner, repo = get_repo_owner_and_name(request.repo_url)
    if not owner or not repo: raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")
    headers = {"Authorization": f"token {request.github_token}", "Accept": "application/vnd.github.v3+json"}
    actions = []
    for finding in request.findings:
        issue_title = f"AI Security Finding: {finding.vulnerability_type} in {finding.file_path}"
        issue_body = (f"**Vulnerability:** {finding.vulnerability_type}...\n") # Omitted for brevity
        issue_payload = {"title": issue_title, "body": issue_body, "labels": ["security", "ai-generated"]}
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            response = requests.post(api_url, headers=headers, json=issue_payload)
            response.raise_for_status()
            issue_data = response.json()
            actions.append(ActionSummary(action_taken="Created GitHub Issue", details=f"Successfully created issue '{issue_data['title']}'", url=issue_data['html_url']))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: raise HTTPException(status_code=401, detail="GitHub API Error: Bad credentials. Please provide a valid GitHub token with 'repo' scope.")
            raise HTTPException(status_code=500, detail=f"Failed to create GitHub issue: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to GitHub API: {str(e)}")
    return TriageResponse(summary=actions)

# --- Agent 4: Software Engineer (UPGRADED WITH ROBUST PARSING) ---
class FixRequest(BaseModel):
    repo_url: str; vulnerability_finding: VulnerabilityFinding; github_token: str
class FixResponse(BaseModel):
    pull_request_url: str; commit_message: str

SOFTWARE_ENGINEER_PROMPT = """You are an expert AI Software Engineer specializing in security. Your task is to fix a security vulnerability in a given snippet of code. You will be provided with a detailed vulnerability report and the exact block of vulnerable source code. Your job is to rewrite the code to fix the vulnerability according to the best security practices. You MUST return a JSON object with two keys: `fixed_code` and `commit_message`. Do not include any other text or explanation in your response."""

@app.post("/fix-vulnerability", response_model=FixResponse)
async def fix_vulnerability(request: FixRequest):
    print(f"Received real fix request for: {request.vulnerability_finding.vulnerability_type}")
    owner, repo = get_repo_owner_and_name(request.repo_url)
    if not owner or not repo: raise HTTPException(status_code=400, detail="Invalid GitHub repo URL.")
    headers = {"Authorization": f"token {request.github_token}", "Accept": "application/vnd.github.v3+json"}
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            repo_path = os.path.join(temp_dir, repo)
            auth_repo_url = f"https://{request.github_token}@github.com/{owner}/{repo}.git"
            subprocess.run(["git", "clone", auth_repo_url, repo_path], check=True, capture_output=True, text=True)
            
            vulnerable_file_path = os.path.join(repo_path, request.vulnerability_finding.file_path)
            if not os.path.exists(vulnerable_file_path): raise HTTPException(status_code=404, detail=f"File not found: {request.vulnerability_finding.file_path}")
            with open(vulnerable_file_path, 'r', encoding='utf-8') as f: vulnerable_code = f.read()
            
            model = genai.GenerativeModel(model_name='gemini-2.5-flash-preview-05-20', system_instruction=SOFTWARE_ENGINEER_PROMPT, generation_config={"response_mime_type": "application/json"})
            finding_json = request.vulnerability_finding.model_dump_json(indent=2)
            user_input = f"Vulnerability Report:\n{finding_json}\n\nVulnerable Code:\n---\n{vulnerable_code}\n---"
            response = model.generate_content(user_input)
            raw_text = response.text
            print(f"--- RAW AI RESPONSE (Fixer) ---\n{raw_text}\n-----------------------")

            # NEW: Robust parsing for the fix data
            try:
                fix_data = json.loads(raw_text)
                if "fixed_code" not in fix_data or "commit_message" not in fix_data:
                    raise HTTPException(status_code=500, detail=f"AI response for fix is missing required keys. Raw: {raw_text}")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"AI returned invalid JSON for the fix. Raw: {raw_text}")

            branch_name = f"ai-fix/{request.vulnerability_finding.vulnerability_type.lower().replace(' ', '-').replace('/', '-')[:20]}"
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True)
            with open(vulnerable_file_path, 'w', encoding='utf-8') as f: f.write(fix_data['fixed_code'])
            subprocess.run(["git", "add", vulnerable_file_path], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", fix_data['commit_message']], cwd=repo_path, check=True)
            subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=repo_path, check=True, capture_output=True, text=True)

            pr_payload = {"title": f"AI Fix: {fix_data['commit_message']}", "head": branch_name, "base": "main", "body": "AI-generated pull request to fix a security vulnerability."}
            api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            pr_response = requests.post(api_url, headers=headers, json=pr_payload)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            return FixResponse(pull_request_url=pr_data['html_url'], commit_message=fix_data['commit_message'])
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: raise HTTPException(status_code=401, detail="GitHub API Error: Bad credentials. Please provide a valid GitHub token with 'repo' scope.")
            raise HTTPException(status_code=500, detail=f"Failed to create pull request: {e.response.text}")
        except subprocess.CalledProcessError as e:
             if "Authentication failed" in e.stderr: raise HTTPException(status_code=401, detail="Git authentication failed. Please provide a valid GitHub token with 'repo' scope.")
             raise HTTPException(status_code=500, detail=f"A git command failed: {e.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during fix/PR process: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

