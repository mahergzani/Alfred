# main.py
# This script orchestrates a team of AI agents to build or update secure software.
# This version includes a stronger prompt for the Tech Lead agent.

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
import subprocess
import tempfile
import shutil
import re 
import requests
import logging

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Configuration ---
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    if not api_key: raise KeyError
    genai.configure(api_key=api_key)
    logging.info("Gemini API configured successfully.")
except KeyError:
    logging.error("GOOGLE_API_KEY not found.")
    exit()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Alfred: AI Software Team API",
    description="Endpoints for an AI team that builds and updates secure software.",
)

# --- CORS Configuration ---
origins = [
    "https://mahergzani.github.io",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(status_code=204)

# --- Security Helper Functions ---
def is_valid_github_url(url: str) -> bool:
    pattern = re.compile(r'^https://github\.com/[\w\-]+/[\w\-\.]+(?:\.git)?$')
    return pattern.match(url) is not None

def get_repo_owner_and_name(repo_url):
    try:
        parts = repo_url.strip().rstrip('.git').split('/')
        return parts[-2], parts[-1]
    except IndexError:
        return None, None

# --- Agent 1: Product Manager ---
class SpecRequest(BaseModel):
    project_idea: str
    existing_code_context: str = ""

class SpecResponse(BaseModel):
    product_spec: str

PRODUCT_MANAGER_PROMPT = """You are an expert AI Product Manager. Your role is to convert a user's high-level project idea or update request into a detailed technical specification. 
If provided, you must consider the context of the existing codebase. The spec should outline user stories, new or modified features, a recommended technology stack (e.g., Python FastAPI backend, React frontend), and data models. The output must be a concise, well-structured markdown string."""

@app.post("/create-spec", response_model=SpecResponse)
async def create_spec(request: SpecRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=PRODUCT_MANAGER_PROMPT)
        user_prompt = f"Project Request: {request.project_idea}"
        if request.existing_code_context:
            user_prompt += f"\n\nHere is the context of the existing project structure and files:\n{request.existing_code_context}"
        response = model.generate_content(user_prompt, request_options={"timeout": 120})
        return SpecResponse(product_spec=response.text)
    except Exception as e:
        logging.error(f"Product Manager agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Product Manager agent timed out or failed: {e}")


# --- Agent 2: Tech Lead / Architect (UPGRADED PROMPT) ---
class ArchRequest(BaseModel):
    product_spec: str
    existing_code_context: str = ""
class FileDetail(BaseModel):
    file_path: str; task: str; reasoning: str
class ArchResponse(BaseModel):
    files_to_modify: List[FileDetail]

# MODIFIED: Prompt is now much more strict to prevent deviation.
TECH_LEAD_PROMPT = """You are an expert AI Tech Lead and Software Architect. Your task is to take a product specification and design the necessary file structure and tasks for a development team.

You will be given the product spec and the context of the existing code.

Your ONLY output MUST be a valid JSON object with a single key "files_to_modify". This key must hold an array of objects.
Each object in the array represents a file to be created or modified and must have three keys:
1. "file_path": A string representing the full path of the file (e.g., "src/main.py").
2. "task": A specific, one-sentence instruction for a developer on what to build or modify in that file.
3. "reasoning": A brief explanation of why this change is necessary.

Do NOT generate an OpenAPI spec. Do NOT write any code. Do NOT include any text outside of the single JSON object.

Example of a valid response:
{
  "files_to_modify": [
    {
      "file_path": "README.md",
      "task": "Create a README.md file that explains the project's purpose and setup instructions.",
      "reasoning": "Provides essential documentation for new developers."
    },
    {
      "file_path": "src/api/endpoints.py",
      "task": "Update the user endpoint to include a new 'profile_picture_url' field.",
      "reasoning": "Adds the user profile picture feature as requested in the spec."
    }
  ]
}
"""

@app.post("/design-architecture", response_model=ArchResponse)
async def design_architecture(request: ArchRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=TECH_LEAD_PROMPT, generation_config={"response_mime_type": "application/json"})
        user_prompt = f"Product Specification:\n{request.product_spec}"
        if request.existing_code_context:
            user_prompt += f"\n\nHere is the context of the existing project structure and files that you need to modify:\n{request.existing_code_context}"
        
        response = model.generate_content(user_prompt, request_options={"timeout": 120})
        raw_text = response.text
        logging.info(f"--- RAW AI RESPONSE (Tech Lead) ---\n{raw_text}\n-----------------------")
        
        response_json = json.loads(raw_text)
        if isinstance(response_json, list):
            response_json = {"files_to_modify": response_json}
        if "files_to_modify" not in response_json:
            raise HTTPException(status_code=500, detail=f"AI response for architecture is missing 'files_to_modify' key. Raw: {raw_text}")
        return ArchResponse.model_validate(response_json)
    except (ValidationError, json.JSONDecodeError) as e:
        logging.error(f"Tech Lead failed to produce valid JSON. Error: {e}. Raw: {response.text if 'response' in locals() else 'No response'}")
        raise HTTPException(status_code=500, detail=f"Tech Lead agent failed to generate a valid architecture plan. Error: {e}")
    except Exception as e:
        logging.error(f"Tech Lead agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tech Lead agent timed out or failed: {e}")


# --- Agent 3: Software Engineer ---
class CodeRequest(BaseModel):
    file_path: str; task: str; existing_code: str = ""
    feedback: str = ""
class CodeResponse(BaseModel):
    code: str

SOFTWARE_ENGINEER_PROMPT = """You are an expert AI Software Engineer. You write clean, functional, and secure code. You will be given a file path, a specific task, and potentially the existing code from that file. 
If you are also given feedback from a QA review, you MUST address that feedback in your new version of the code.
Your job is to write the complete, updated code for that file to accomplish the task, incorporating any feedback. If existing code is provided, modify it as needed. If not, create it from scratch. 
Only output the raw, complete code for the file. Do not include any explanation, markdown formatting, or any text other than the code itself."""

@app.post("/write-code", response_model=CodeResponse)
async def write_code(request: CodeRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=SOFTWARE_ENGINEER_PROMPT)
        user_prompt = f"File Path: {request.file_path}\nTask: {request.task}"
        if request.existing_code:
            user_prompt += f"\n\nHere is the existing code for that file that you must modify:\n```\n{request.existing_code}\n```"
        if request.feedback:
            user_prompt += f"\n\IMPORTANT: Your previous attempt was rejected. You MUST fix the following issues:\n{request.feedback}"
        
        response = model.generate_content(user_prompt, request_options={"timeout": 120})
        cleaned_code = response.text.strip()
        if cleaned_code.startswith("```") and cleaned_code.endswith("```"):
            cleaned_code = '\n'.join(cleaned_code.split('\n')[1:-1])
        return CodeResponse(code=cleaned_code)
    except Exception as e:
        logging.error(f"Software Engineer agent failed for file {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Software Engineer agent timed out or failed for {request.file_path}: {e}")


# --- Agent 4: QA & Security Engineer ---
class ReviewRequest(BaseModel):
    file_path: str; code_to_review: str
class ReviewResponse(BaseModel):
    approved: bool; feedback: str

QA_SECURITY_PROMPT = """You are an expert QA and Security Engineer. You review code for bugs and security vulnerabilities. You will be given a file path and its code. If the code is high-quality, functional, and secure, respond with a JSON object: `{"approved": true, "feedback": "Code looks good and follows security best practices."}`. If you find any issues, respond with `{"approved": false, "feedback": "A detailed, constructive explanation of the issues found."}`."""

@app.post("/review-code", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=QA_SECURITY_PROMPT, generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(f"File to Review: {request.file_path}\n\nCode:\n{request.code_to_review}", request_options={"timeout": 120})
        return ReviewResponse.model_validate_json(response.text)
    except (ValidationError, json.JSONDecodeError) as e:
        logging.error(f"QA agent failed to produce valid JSON. Raw: {response.text if 'response' in locals() else 'No response'}")
        raise HTTPException(status_code=500, detail="QA agent failed to generate a valid review.")
    except Exception as e:
        logging.error(f"QA agent failed for file {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"QA agent timed out or failed for {request.file_path}: {e}")


# --- Final Step: Create Pull Request ---
class PRRequest(BaseModel):
    repo_url: str; github_token: str; project_idea: str
class PRResponse(BaseModel):
    pull_request_url: str

@app.post("/create-pull-request", response_model=PRResponse)
async def create_pull_request(request: PRRequest):
    logging.info("\n--- [START] AI Butler Service Request ---")
    if not is_valid_github_url(request.repo_url):
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format.")

    owner, repo = get_repo_owner_and_name(request.repo_url)
    if not owner or not repo: raise HTTPException(status_code=400, detail="Invalid GitHub repo URL.")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            repo_path = os.path.join(temp_dir, repo)
            auth_repo_url = f"https://{request.github_token}@github.com/{owner}/{repo}.git"
            
            logging.info("--> [Step 1/7] Cloning repository...")
            subprocess.run(["git", "clone", auth_repo_url, repo_path], check=True, capture_output=True, timeout=60)
            logging.info("<-- [Step 1/7] Repository cloned successfully.")
            
            existing_code_context = ""
            for root, _, files in os.walk(repo_path):
                for file in files:
                    if ".git" in root: continue
                    relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                    existing_code_context += f"- {relative_path}\n"

            logging.info("--> [Step 2/7] Engaging Product Manager to create spec...")
            spec_response = await create_spec(SpecRequest(project_idea=request.project_idea, existing_code_context=existing_code_context))
            logging.info("<-- [Step 2/7] Product Manager finished.")
            
            logging.info("--> [Step 3/7] Engaging Tech Lead to design architecture...")
            arch_response = await design_architecture(ArchRequest(product_spec=spec_response.product_spec, existing_code_context=existing_code_context))
            logging.info(f"<-- [Step 3/7] Tech Lead finished. Plan involves {len(arch_response.files_to_modify)} file(s).")

            branch_name = f"feat/ai-update-{request.project_idea.lower().replace(' ', '-')[:20]}"
            logging.info(f"--> [Step 4/7] Creating new branch: {branch_name}...")
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True)
            logging.info(f"<-- [Step 4/7] Branch created.")

            logging.info("--> [Step 5/7] Engaging Software Engineer with Self-Correction Loop...")
            for i, file_detail in enumerate(arch_response.files_to_modify):
                logging.info(f"    - ({i+1}/{len(arch_response.files_to_modify)}) Processing {file_detail.file_path}...")
                file_path = os.path.join(repo_path, file_detail.file_path)
                existing_code = ""
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_code = f.read()
                
                max_retries = 3; current_feedback = ""; approved = False; final_code = ""

                for attempt in range(max_retries):
                    logging.info(f"      - Attempt {attempt + 1}/{max_retries}: Engineer writing code...")
                    code_response = await write_code(CodeRequest(file_path=file_detail.file_path, task=file_detail.task, existing_code=existing_code if attempt == 0 else final_code, feedback=current_feedback))
                    
                    logging.info(f"      - Attempt {attempt + 1}/{max_retries}: QA reviewing code...")
                    review_response = await review_code(ReviewRequest(file_path=file_detail.file_path, code_to_review=code_response.code))
                    
                    if review_response.approved:
                        logging.info(f"      - Attempt {attempt + 1}/{max_retries}: QA Approved!")
                        approved = True; final_code = code_response.code; break
                    else:
                        logging.warning(f"      - Attempt {attempt + 1}/{max_retries}: QA Rejected. Feedback: {review_response.feedback}")
                        current_feedback = review_response.feedback; final_code = code_response.code
                
                if not approved:
                    raise HTTPException(status_code=400, detail=f"QA agent failed to approve code for {file_detail.file_path} after {max_retries} attempts. Last feedback: {current_feedback}")
                
                logging.info(f"    - Saving approved code for {file_detail.file_path}.")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f: f.write(final_code)

            logging.info("<-- [Step 5/7] Software Engineer finished writing all files.")
            
            logging.info("--> [Step 6/7] Committing and pushing changes to GitHub...")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", f"feat: AI-generated update for '{request.project_idea}'"], cwd=repo_path, check=True)
            subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=repo_path, check=True, capture_output=True, text=True)
            logging.info("<-- [Step 6/7] Changes pushed successfully.")
            
            logging.info("--> [Step 7/7] Creating Pull Request...")
            headers = {"Authorization": f"token {request.github_token}", "Accept": "application/vnd.github.v3+json"}
            pr_payload = {"title": f"AI Update: {request.project_idea}", "head": branch_name, "base": "main", "body": "This is an AI-generated pull request containing updates to the software."}
            api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            pr_response = requests.post(api_url, headers=headers, json=pr_payload, timeout=30)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            logging.info("<-- [Step 7/7] Pull Request created.")
            
            logging.info("--- [END] AI Butler Service Request Successful ---")
            return PRResponse(pull_request_url=pr_data['html_url'])
        
        except subprocess.TimeoutExpired:
            logging.error("A git command timed out.")
            raise HTTPException(status_code=500, detail="A git command timed out.")
        except Exception as e:
            error_detail = str(e)
            if hasattr(e, 'stderr'): error_detail = e.stderr
            if hasattr(e, 'response'): error_detail = e.response.text
            logging.error(f"--- [END] AI Butler Service Request FAILED ---\nERROR: {error_detail}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {error_detail}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

