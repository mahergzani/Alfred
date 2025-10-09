# Alfred - AI-Powered Software Development Team

Alfred orchestrates a team of specialized AI agents to autonomously build and develop secure software based on a high-level user request. It follows a modern software development lifecycle (SDLC) where security is an integral part of every step.

## 🚀 Quick Start

**Ready to run Alfred on your device?** See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

**TL;DR:**
```bash
git clone https://github.com/mahergzani/Alfred.git
cd Alfred/backend
cp .env.example .env  # Add your GOOGLE_API_KEY
./start.sh  # On macOS/Linux, or start.bat on Windows
```

Then visit: http://localhost:8000-Powered Software Development Team
This project orchestrates a team of specialized AI agents to autonomously build and develop secure software based on a high-level user request. It follows a modern software development lifecycle (SDLC) where security is an integral part of every step.

The AI Agent Team
The application coordinates a workflow between four distinct AI agents:

Product Manager Agent:

Input: A high-level software idea (e.g., "a secure personal diary web app").

Responsibility: Translates the idea into a detailed technical specification, outlining user stories, key features, and a proposed technology stack.

Tech Lead / Architect Agent:

Input: The technical specification from the Product Manager.

Responsibility: Designs the complete software architecture. This includes defining the file structure, database models, API endpoints, and embedding security best practices (like authentication, data validation, etc.) directly into the design.

Software Engineer Agent:

Input: A specific task from the Tech Lead (e.g., "write the code for the user login API endpoint").

Responsibility: Writes the functional, secure code for the assigned file and task.

QA & Security Engineer Agent:

Input: The code written by the Software Engineer.

Responsibility: Performs a final review of the code to catch any functional bugs or security vulnerabilities before the code is committed, acting as a final quality and security gate.

The Workflow
The web application guides these agents through the following automated process:

Specification: The Product Manager agent creates a detailed plan.

Architecture: The Tech Lead agent designs the structure of the new software.

Development: For each file in the architecture plan, the Software Engineer agent writes the code.

Review: The QA & Security agent reviews the newly written code.

Commit & Propose: If the code passes review, it is automatically committed to a new branch, and a pull request is created for human oversight.