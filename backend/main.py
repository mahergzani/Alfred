# main.py
# This script orchestrates a team of AI agents to build secure software.

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List
import json
import subprocess
import tempfile

# --- Configuration ---
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")
except KeyError:
    print("ERROR: GOOGLE_API_KEY not found.")
    exit()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Software Development Team API",
    description="Endpoints for an AI team that builds secure software.",
)

# --- CORS Configuration ---
origins = ["https://mahergzani.github.io", "http://localhost:8000", "http://127.0.0.1:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(status_code=204)

# --- Helper Function ---
def get_repo_owner_and_name(repo_url):
    try:
        parts = repo_url.strip().rstrip('.git').split('/')
        return parts[-2], parts[-1]
    except IndexError:
        return None, None

# --- Agent 1: Product Manager ---
class SpecRequest(BaseModel):
    project_idea: str

class SpecResponse(BaseModel):
    product_spec: str

PRODUCT_MANAGER_PROMPT = """You are an expert AI Product Manager. Your role is to convert a user's high-level project idea into a detailed technical specification. The spec should outline user stories, core features, a recommended technology stack (e.g., Python FastAPI backend, React frontend), and data models. The output must be a concise, well-structured markdown string."""

@app.post("/create-spec", response_model=SpecResponse)
async def create_spec(request: SpecRequest):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=PRODUCT_MANAGER_PROMPT)
    response = model.generate_content(f"Project Idea: {request.project_idea}")
    return SpecResponse(product_spec=response.text)


# --- Agent 2: Tech Lead / Architect ---
class ArchRequest(BaseModel):
    product_spec: str

class FileDetail(BaseModel):
    file_path: str
    task: str

class ArchResponse(BaseModel):
    files: List[FileDetail]

TECH_LEAD_PROMPT = """You are an expert AI Tech Lead and Software Architect. Your task is to take a product specification and design the software architecture. You MUST output a JSON object containing a single key "files". This key should hold an array of objects, where each object has two keys: "file_path" (e.g., "src/main.py") and "task" (a specific, one-sentence instruction for a junior developer on what to build in that file, including security considerations). Ensure your architecture includes necessary files like Dockerfile, .gitignore, and requirements.txt."""

@app.post("/design-architecture", response_model=ArchResponse)
async def design_architecture(request: ArchRequest):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=TECH_LEAD_PROMPT, generation_config={"response_mime_type": "application/json"})
    response = model.generate_content(f"Product Specification:\n{request.product_spec}")
    return ArchResponse.model_validate_json(response.text)


# --- Agent 3: Software Engineer ---
class CodeRequest(BaseModel):
    file_path: str
    task: str

class CodeResponse(BaseModel):
    code: str

SOFTWARE_ENGINEER_PROMPT = """You are an expert AI Software Engineer. You write clean, functional, and secure code. You will be given a file path and a specific task. Your job is to write the complete code for that file to accomplish the task. Your code should be production-ready. Only output the raw code for the file. Do not include any explanation, markdown formatting, or any text other than the code itself."""

@app.post("/write-code", response_model=CodeResponse)
async def write_code(request: CodeRequest):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=SOFTWARE_ENGINEER_PROMPT)
    response = model.generate_content(f"File Path: {request.file_path}\nTask: {request.task}")
    # Clean up potential markdown code blocks
    cleaned_code = response.text.strip()
    if cleaned_code.startswith("```") and cleaned_code.endswith("```"):
        lines = cleaned_code.split('\n')
        cleaned_code = '\n'.join(lines[1:-1])
    return CodeResponse(code=cleaned_code)


# --- Agent 4: QA & Security Engineer ---
class ReviewRequest(BaseModel):
    file_path: str
    code_to_review: str

class ReviewResponse(BaseModel):
    approved: bool
    feedback: str

QA_SECURITY_PROMPT = """You are an expert QA and Security Engineer. You review code for bugs and security vulnerabilities. You will be given a file path and its code. If the code is high-quality, functional, and secure, respond with a JSON object: `{"approved": true, "feedback": "Code looks good."}`. If you find any issues, respond with `{"approved": false, "feedback": "A detailed, constructive explanation of the issues found."}`."""

@app.post("/review-code", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=QA_SECURITY_PROMPT, generation_config={"response_mime_type": "application/json"})
    response = model.generate_content(f"File to Review: {request.file_path}\n\nCode:\n{request.code_to_review}")
    return ReviewResponse.model_validate_json(response.text)
    
    
# --- Final Step: Create Pull Request ---
class PRRequest(BaseModel):
    repo_url: str
    github_token: str
    architecture: ArchResponse
    project_idea: str

class PRResponse(BaseModel):
    pull_request_url: str

@app.post("/create-pull-request", response_model=PRResponse)
async def create_pull_request(request: PRRequest):
    owner, repo = get_repo_owner_and_name(request.repo_url)
    if not owner or not repo: raise HTTPException(status_code=400, detail="Invalid GitHub repo URL.")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            repo_path = os.path.join(temp_dir, repo)
            auth_repo_url = f"https://{request.github_token}@github.com/{owner}/{repo}.git"
            
            # Initialize a new git repo locally, as the remote one is empty
            subprocess.run(["git", "init"], cwd=repo_path, check=True)
            
            # Generate code for all files
            for file_detail in request.architecture.files:
                code_response = await write_code(CodeRequest(file_path=file_detail.file_path, task=file_detail.task))
                file_path = os.path.join(repo_path, file_detail.file_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code_response.code)

            # Commit and Push
            branch_name = "feat/initial-build-by-ai"
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True)
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", f"feat: Initial AI-generated build for '{request.project_idea}'"], cwd=repo_path, check=True)
            subprocess.run(["git", "remote", "add", "origin", auth_repo_url], cwd=repo_path, check=True)
            subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=repo_path, check=True, capture_output=True, text=True)
            
            # Create Pull Request
            headers = {"Authorization": f"token {request.github_token}", "Accept": "application/vnd.github.v3+json"}
            pr_payload = {"title": f"AI Initial Build: {request.project_idea}", "head": branch_name, "base": "main", "body": "This is an AI-generated pull request containing the initial software build."}
            api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            pr_response = requests.post(api_url, headers=headers, json=pr_payload)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            return PRResponse(pull_request_url=pr_data['html_url'])
        
        except (subprocess.CalledProcessError, requests.exceptions.RequestException, Exception) as e:
            error_detail = str(e)
            if hasattr(e, 'stderr'): error_detail = e.stderr
            if hasattr(e, 'response'): error_detail = e.response.text
            print(f"ERROR during PR process: {error_detail}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {error_detail}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

