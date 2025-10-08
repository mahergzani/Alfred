# main.py
# This script orchestrates a team of AI agents to build or update software conversationally.

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
from typing import List, Dict
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

# --- Agent 1: Product Manager ---
class SpecRequest(BaseModel):
    project_idea: str
    conversation_history: List[ChatMessage] = []

class SpecResponse(BaseModel):
    product_spec: str

PRODUCT_MANAGER_PROMPT = """You are an expert AI Product Manager in a conversation with a user. Your role is to analyze the entire conversation history and produce a detailed technical specification for the software they want to build. The specification should outline user stories, features, and data models. If the user provides feedback or asks for changes, refine the spec accordingly. Your output should be a concise, well-structured markdown string containing the complete spec."""

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

TECH_LEAD_PROMPT = """You are an expert AI Tech Lead and Software Architect. Your task is to take a product specification and design the necessary file structure and tasks for a development team.
For any features involving authentication or user data, you MUST include specific security requirements in the "task" description, such as password hashing methodologies, token handling, and rate limiting.
Your ONLY output MUST be a valid JSON object with a single key "files_to_modify". This key must hold an array of objects.
Each object in the array represents a file to be created or modified and must have three keys:
1. "file_path": A string representing the full path of the file (e.g., "src/main.py").
2. "task": A specific, one-sentence instruction for a developer on what to build or modify in that file.
3. "reasoning": A brief explanation of why this change is necessary.
Do NOT write any code. Do NOT include any text outside of the single JSON object."""

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

SOFTWARE_ENGINEER_PROMPT = """You are an expert AI Software Engineer. You write clean, functional, and secure code.
You are expected to be proactive about security. When implementing features like authentication or data handling, you must use security best practices by default, even if not explicitly stated in the task.
You will be given a file path, a specific task, and potentially the existing code from that file. 
If you are also given feedback from a QA review, you MUST address that feedback in your new version of the code.
Your job is to write the complete, updated code for that file to accomplish the task.
Only output the raw, complete code for the file. Do not include any explanation, markdown formatting, or any text other than the code itself."""

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

QA_SECURITY_PROMPT = """You are an expert QA and Security Engineer. You review code for bugs and security vulnerabilities. You will be given a file path and its code. If the code is high-quality, functional, and secure, respond with a JSON object: `{"approved": true, "feedback": "Code looks good and follows security best practices."}`. If you find any issues, respond with `{"approved": false, "feedback": "A detailed, constructive explanation of the issues found."}`."""

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

        async def log_and_queue(message, level=logging.INFO):
            if level == logging.INFO: logging.info(message)
            elif level == logging.WARNING: logging.warning(message)
            elif level == logging.ERROR: logging.error(message)
            
            log_queue.put_nowait(f"data: {message}\n\n")
            await asyncio.sleep(0.01)

        async def run_build():
            try:
                await log_and_queue("--- [START] AI Butler Service Request ---")
                
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
                        eng_prompt = f"File Path: {file_path}\nTask: {task}"
                        if feedback: eng_prompt += f"\n\IMPORTANT: Your previous attempt was rejected. You MUST fix the following issues:\n{feedback}"
                        
                        code_response = await eng_model.generate_content_async(eng_prompt, request_options={"timeout": 180})
                        generated_code = code_response.text.strip()
                        if generated_code.startswith("```") and generated_code.endswith("```"):
                            cleaned_code = '\n'.join(generated_code.split('\n')[1:-1])
                            generated_code = cleaned_code.strip()

                        await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: QA reviewing code...")
                        qa_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20', system_instruction=QA_SECURITY_PROMPT)
                        qa_prompt = f"File to Review: {file_path}\n\nCode:\n{generated_code}"
                        
                        # QA review with JSON retry logic
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
                            generated_files[file_path] = generated_code
                            file_data = json.dumps({"path": file_path, "content": generated_code})
                            await log_queue.put(f"data: [FILE]{file_data}\n\n")
                            approved = True
                            break
                        else:
                            feedback = review.get("feedback", "No feedback provided.")
                            await log_and_queue(f"        - Attempt {attempt + 1}/{max_retries}: QA Rejected. Feedback: {feedback[:200]}...", level=logging.WARNING)

                    if not approved:
                        raise Exception(f"QA failed to approve code for {file_path} after {max_retries} attempts.")
                
                await log_and_queue("<-- [Step 3/4] All files generated successfully.")
                await log_and_queue("--> [Step 4/4] Build complete. Ready for download.")
                await log_queue.put("data: [DONE]\n\n")

            except Exception as e:
                error_detail = str(e)
                await log_and_queue(f"--- [END] AI Butler Service Request FAILED ---\nERROR: {error_detail}", level=logging.ERROR)
                await log_queue.put(f"data: [ERROR] {error_detail}\n\n")
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