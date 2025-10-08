# main.py
# This script orchestrates a team of AI agents to build or update software conversationally.

import uuid
from datetime import datetime
from fastapi.responses import StreamingResponse
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Optional
import json
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
origins = ["*"]
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

# --- Pydantic Models for Conversational Build ---
class ChatMessage(BaseModel):
    role: str
    content: str

class BuildRequest(BaseModel):
    history: List[ChatMessage]
    session_id: Optional[str] = None

# --- Agent 1: Product Manager ---
class SpecRequest(BaseModel):
    project_idea: str
    conversation_history: List[ChatMessage] = []

class SpecResponse(BaseModel):
    product_spec: str

PRODUCT_MANAGER_PROMPT = """
You are an expert AI Product Manager. Your primary goal is to collaborate with a user through conversation to create a detailed technical specification for a software project.

Core Task
Analyze the entire conversation history to produce or update a comprehensive technical specification. The spec must include:

User Stories: Clearly define the users and what they need to accomplish.

Features: Detail the specific features required to fulfill the user stories.

Data Models: Describe the necessary data structures, fields, and relationships.

Conversational Behavior
Ask for Clarification: If the user's request is ambiguous, incomplete, or contradictory, your first priority is to ask targeted, clarifying questions. Do not invent details to fill in the gaps.

Refine and Iterate: When the user provides feedback or requests changes, refine the specification and present the new, complete version in your response.

Output Format
Your entire response must be a single, concise, and well-structured Markdown string. Your response should contain either the complete technical specification or your clarifying questions.
"""

@app.post("/create-spec", response_model=SpecResponse)
async def create_spec(request: SpecRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=PRODUCT_MANAGER_PROMPT)
        prompt = f"Here is the conversation history. Please produce a complete technical specification based on it:\n\n{json.dumps([msg.dict() for msg in request.conversation_history])}"
        response = model.generate_content(prompt, request_options={"timeout": 180})
        return SpecResponse(product_spec=response.text)
    except Exception as e:
        logging.error(f"Product Manager agent failed: {e}")
        raise HTTPException(status_code=500, detail=f"Product Manager agent timed out or failed: {e}")

# --- Agent 2: Tech Lead / Architect ---
class ArchRequest(BaseModel):
    product_spec: str
class FileDetail(BaseModel):
    file_path: str
    task: str
    reasoning: str
class ArchResponse(BaseModel):
    files_to_modify: List[FileDetail]

TECH_LEAD_PROMPT = """
Of course. Here is a cleaned-up and more robust version of the Tech Lead prompt that organizes the rules into a clearer, more logical structure.

You are an expert AI Tech Lead and Software Architect. Your primary function is to translate a product specification into a detailed, actionable plan for a software engineering team.

Output Format
Your ONLY output MUST be a single, valid JSON object. This object must adhere to the following strict structure:

A single root key named "files_to_modify".

The value of "files_to_modify" must be an array of objects.

Each object in the array represents one file and MUST have exactly three keys:

"file_path": (string) The full, relative path to the file (e.g., "src/controllers/auth.js").

"task": (string) A clear, specific, and actionable instruction for the engineer.

"reasoning": (string) A concise explanation for why the file or change is needed.

Task Content Requirements
When defining the "task" for each file, you MUST adhere to the following principles:

Security by Design: For any features involving authentication, user data, or API endpoints, the task must explicitly specify the required security measures (e.g., "Implement password hashing using bcrypt," "Add rate limiting to the login endpoint," "Validate all request body fields.").

Completeness: Tasks must describe production-ready features. Do not specify tasks that use placeholders or mock functionality, especially for critical areas like permissions or authentication.

Robustness: Tasks for API endpoints must include a requirement for strict validation of all user-supplied data (URL parameters, query strings, and request bodies).

Final Constraints
Do NOT write any code.

Do NOT include any text, notes, or explanations outside of the final JSON object.
"""

@app.post("/design-architecture", response_model=ArchResponse)
async def design_architecture(request: ArchRequest):
    # This function remains for modularity but its logic is used in the main endpoint.
    pass

# --- Agent 3: Software Engineer ---
class CodeRequest(BaseModel):
    file_path: str
    task: str
    existing_code: str = ""
    feedback: str = ""
class CodeResponse(BaseModel):
    code: str

SOFTWARE_ENGINEER_PROMPT = """
You are an expert AI Software Engineer who writes clean, functional, and secure production-ready code.

Core Directives
Your ONLY output is the raw, complete code for the specified file. Do not include any explanations, markdown formatting, or any text other than the code itself.

Your code must be complete and functional. DO NOT use placeholder or mock implementations, especially for critical features like permissions, database interactions, or authentication.

Guiding Principles
1. Security First
You are expected to be proactive about security and apply best practices by default, even if not explicitly stated in the task.

Input Validation: You MUST implement strict input validation for all user-controlled data. Never trust user input. Sanitize and validate data from request bodies, query parameters, and URL paths.

Sensitive Data: Never store sensitive data (passwords, API keys, refresh tokens) in plaintext. Always hash them using a strong, modern algorithm like bcrypt or Argon2.

Data Updates: Use a whitelist approach for updating data (e.g., const { name, email } = req.body;) rather than a blacklist (delete req.body.id;) to prevent mass assignment vulnerabilities.

Database Integrity: Ensure database relationships and cascade settings do not lead to unintentional data loss.

Least Privilege: Ensure functions and API endpoints only have access to the data they absolutely need.

2. Production Readiness
No Debug Statements: Your code must not contain any console.log, print, or other debug statements.

Appropriate Storage: Use appropriate storage mechanisms for file uploads (e.g., disk or cloud storage, not in-memory storage).

Structured Logging: Employ structured and configurable logging for errors and important events.

Task Execution
You will receive a file path, a specific task, and optionally, the existing code for that file. If you are also given feedback from a QA review, you MUST address all points from the feedback in your new version of the code. Your job is to write the complete, updated code that accomplishes the task according to all the principles above.
"""

@app.post("/write-code", response_model=CodeResponse)
async def write_code(request: CodeRequest):
    # This function remains for modularity but its logic is used in the main endpoint.
    pass

# --- Agent 4: QA & Security Engineer ---
class ReviewRequest(BaseModel):
    file_path: str
    code_to_review: str
class ReviewResponse(BaseModel):
    approved: bool
    feedback: str

QA_SECURITY_PROMPT = """
You are an expert QA and Security Engineer. Your primary function is to perform a thorough review of a given code file, identifying bugs, security vulnerabilities, and areas for improvement.

Review Criteria
You must evaluate the code based on the following criteria, in order of importance:

Security: Is the code free of vulnerabilities? Check for common issues like SQL injection, improper input validation, missing authentication/authorization, insecure data storage (e.g., plaintext tokens), and potential race conditions.

Functionality: Does the code correctly implement its intended logic? Are there bugs, logical errors, or unhandled edge cases?

Code Quality: Does the code follow best practices for readability, maintainability, and performance?

Output Format
Your ONLY output MUST be a single, valid JSON object. The object MUST have exactly two keys:

"approved": (boolean) Set to true only if the code is completely secure and functional. If there are any security vulnerabilities or major bugs, this must be false.

"feedback": (string) A detailed explanation of your findings, following the requirements below.

Feedback Requirements
If "approved" is true, the feedback should be a simple confirmation (e.g., "Code is secure and follows best practices.").

If "approved" is false, the feedback MUST be a detailed and constructive report that:

Clearly separates Critical Security Vulnerabilities from Minor Suggestions or code quality improvements.

Explains the impact of each issue (i.e., why it's a problem).

Provides specific and actionable recommendations on how to fix the issues.
"""

@app.post("/review-code", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    # This function remains for modularity but its logic is used in the main endpoint.
    pass

# --- Main Build Orchestrator ---
@app.post("/build-project")
async def build_project(request: BuildRequest):
    async def log_streamer():
        log_queue = asyncio.Queue()
        generated_files: Dict[str, str] = {}

        async def log_and_queue(message, level=logging.INFO, is_raw=False):
            # Log to console for backend debugging
            if not is_raw:
                if level == logging.INFO: logging.info(message)
                elif level == logging.WARNING: logging.warning(message)
                elif level == logging.ERROR: logging.error(message)
            
            # Put the message in the queue for the browser, wrapping it in the SSE format
            log_queue.put_nowait(f"data: {message}\n\n")
            # Add a small delay to allow the message to be sent and the UI to update
            await asyncio.sleep(0.01)

        async def run_build():
            try:
                session_id = request.session_id # This will be None on a new request
                # --- NEW: SESSION AND FOLDER HANDLING ---
                if session_id:
                    project_path = os.path.join("project_builds", session_id)
                    # Check if the folder exists (safety check for continuing session)
                    if os.path.exists(project_path):
                        await log_and_queue(f"[SESSION_ID]{session_id}", is_raw=True)
                        await log_and_queue(f"Continuing session: {session_id}")
                    else:
                         # Client provided an ID but the folder doesn't exist (can happen)
                         os.makedirs(project_path, exist_ok=True)
                         await log_and_queue(f"[SESSION_ID]{session_id}", is_raw=True)
                         await log_and_queue(f"Starting NEW session with client ID: {session_id}")
                else:
                    # No session_id provided: Server generates a new one
                    session_id = str(uuid.uuid4())
                    project_path = os.path.join("project_builds", session_id)
                    os.makedirs(project_path, exist_ok=True)
                    
                    # The client MUST consume this message to store the new ID
                    await log_and_queue(f"[SESSION_ID]{session_id}", is_raw=True) 
                    await log_and_queue(f"Starting new session: {session_id}")
                # --- END SESSION HANDLING ---

                await log_and_queue("--- [START] AI Butler Service Request ---")
                
                # --- NEW: Create a directory for QA reports ---
                os.makedirs("qa_reports", exist_ok=True)
                
                # Agent 1: Product Manager
                await log_and_queue("--> [Step 1/4] Engaging Product Manager...")
                pm_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=PRODUCT_MANAGER_PROMPT)
                pm_prompt = "Here is the conversation history. Please produce a complete technical specification based on it:\n\n" + json.dumps([msg.dict() for msg in request.history])
                pm_response = await pm_model.generate_content_async(pm_prompt, request_options={"timeout": 180})
                product_spec = pm_response.text
                await log_and_queue("<-- [Step 1/4] Product Manager finished.")
                await log_and_queue(f"**Spec Summary:**\n{product_spec[:400]}...")

                # Agent 2: Tech Lead
                await log_and_queue("--> [Step 2/4] Engaging Tech Lead...")
                tl_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=TECH_LEAD_PROMPT)
                tl_prompt = f"Product Specification:\n{product_spec}"
                tl_response = await tl_model.generate_content_async(tl_prompt, request_options={"timeout": 180}, generation_config={"response_mime_type": "application/json"})
                arch_response = json.loads(tl_response.text)
                files_to_modify = arch_response.get("files_to_modify", [])
                await log_and_queue(f"<-- [Step 2/4] Tech Lead finished. Plan involves {len(files_to_modify)} file(s).")

                # Agents 3 & 4: Engineer & QA Loop
                await log_and_queue("--> [Step 3/4] Engaging Software Engineer & QA...")
                max_retries = 3
                for i, file_detail in enumerate(files_to_modify):
                    file_path = file_detail["file_path"]
                    task = file_detail["task"]
                    await log_and_queue(f"    - ({i+1}/{len(files_to_modify)}) Processing {file_path}...")
                    feedback = ""
                    approved = False
                    
                    for attempt in range(max_retries):
                        await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: Engineer writing code...")
                        eng_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=SOFTWARE_ENGINEER_PROMPT)
                        eng_prompt = f"""File Path: {file_path}
                        Task: {task}"""
                        if feedback:
                            eng_prompt += f"""

                        IMPORTANT: Your previous attempt was rejected. You MUST fix the following issues:
                        {feedback}"""
    
                        code_response = await eng_model.generate_content_async(eng_prompt, request_options={"timeout": 180})
                        generated_code = code_response.text.strip()
                        if generated_code.startswith("```") and generated_code.endswith("```"):
                            cleaned_code = '\n'.join(generated_code.split('\n')[1:-1])
                            generated_code = cleaned_code.strip()

                        await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: QA reviewing code...")
                        qa_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=QA_SECURITY_PROMPT)
                        qa_prompt = f"File to Review: {file_path}\n\nCode:\n{generated_code}"
                        
                        review = None
                        for qa_attempt in range(max_retries):
                            try:
                                qa_response_raw = await qa_model.generate_content_async(qa_prompt, request_options={"timeout": 180}, generation_config={"response_mime_type": "application/json"})
                                review = json.loads(qa_response_raw.text)
                                break 
                            except (ValidationError, json.JSONDecodeError) as e:
                                await log_and_queue(f"        - QA agent produced invalid JSON on attempt {qa_attempt + 1}. Retrying.", level=logging.WARNING)
                                if qa_attempt == max_retries - 1: raise e
                        
                        if review and review.get("approved"):
                            await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: QA Approved!")

                            # --- NEW: SAVE FILE TO DISK ---
                            full_disk_path = os.path.join(project_path, file_path)
                            os.makedirs(os.path.dirname(full_disk_path), exist_ok=True)
                            with open(full_disk_path, "w") as f:
                                f.write(generated_code)
                            
                            # Stream the file to the frontend for the zip download
                            file_data_json = json.dumps({"path": file_path, "content": generated_code})
                            await log_and_queue(f"[FILE]{file_data_json}", is_raw=True)
                            
                            approved = True
                            break
                        else:
                            feedback = review.get("feedback", "No feedback provided.")
                            
                            # --- NEW: Save the full QA report to a file ---
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            safe_file_path = file_path.replace('/', '_').replace('\\', '_')
                            report_filename = f"qa_reports/qa_report_{timestamp}_{safe_file_path}_attempt_{attempt + 1}.txt"
                            with open(report_filename, "w") as f:
                                f.write(feedback)
                            await log_and_queue(f"        - Full QA report saved to {report_filename}", level=logging.INFO)
                            
                            # This is the original truncated log for the live view
                            await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: QA Rejected. Feedback: {feedback[:200]}...", level=logging.WARNING)

                    if not approved:
                        raise Exception(f"QA failed to approve code for {file_path} after {max_retries} attempts.")
                
                await log_and_queue("<-- [Step 3/4] All files generated successfully.")
                await log_and_queue("--> [Step 4/4] Build complete. Ready for download.")
                await log_and_queue("[DONE]", is_raw=True)
                # Add a small delay to ensure the [DONE] message is sent before the stream closes.
                await asyncio.sleep(0.1)

            except Exception as e:
                error_detail = str(e)
                await log_and_queue(f"--- [END] AI Butler Service Request FAILED ---\nERROR: {error_detail}", level=logging.ERROR)
                await log_and_queue(f"[ERROR] {error_detail}", is_raw=True)
            finally:
                await log_queue.put(None)

        asyncio.create_task(run_build())

        while True:
            message = await log_queue.get()
            if message is None:
                break
            yield message

    return StreamingResponse(log_streamer(), media_type="text/event-stream")

# --- Run the App ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)