# **Getting Started Guide**

This guide will help you set up and run the AI-Powered Security Audit web application. The core of this project is the interaction between the frontend and a team of AI agents.

## **Prerequisites**

1. **Web Hosting:** You need a place to host the index.html file. A static hosting provider like Netlify, Vercel, or GitHub Pages is perfect for this.  
2. **Google Agent Development Kit (or similar):** This project assumes you have a backend service where your AI agents are built and exposed via API endpoints. The frontend JavaScript will need to be updated to call these real endpoints instead of the mock functions.  
3. **GitHub API Access:** To perform actions like creating issues and pull requests, your backend agents will need a GitHub Personal Access Token with the appropriate permissions (repo, workflow).

## **Step 1: Frontend Setup**

1. **Host index.html:** Upload the index.html file to your chosen hosting provider.  
2. **No further frontend setup is needed** as all styles and scripts are self-contained.

## **Step 2: Backend AI Agent Setup**

This is the most critical part of the setup. The index.html file contains mock JavaScript functions that simulate the agents. You need to replace these with real API calls to your agents.

1. **Build Your Agents:** Using a framework like the Google Agent Development Kit, create four separate agents, each with the persona and responsibilities outlined in the README.md file.  
   * **Security Manager Agent:** Takes a string (strategic goal) and returns a string (tactical plan).  
   * **Penetration Tester Agent:** Takes a tactical plan and a repo URL, and returns a detailed vulnerability report (string or JSON).  
   * **Security Engineer Agent:** Takes a vulnerability report and a repo URL. It should perform actions against the GitHub API (creating issues, adding files) and return a summary of its actions.  
   * **Software Engineer Agent:** Takes a list of issues and a repo URL. It should perform actions against the GitHub API (committing code, creating PRs) and return the URL of the updated repository.  
2. **Expose Agents via API:** Create an API endpoint for each agent. For example:  
   * POST /api/run-security-manager  
   * POST /api/run-pen-tester  
   * POST /api/run-security-engineer  
   * POST /api/run-software-engineer

## **Step 3: Connect Frontend to Backend**

1. **Edit index.html:** Open the index.html file and find the \<script\> section at the bottom.  
2. **Replace Mock Functions:** Replace the placeholder runSecurityManager, runPenTester, runSecurityEngineer, and runSoftwareEngineer functions with fetch calls to your new API endpoints.

**Example of replacing a mock function:**

// \--- BEFORE \---  
const runSecurityManager \= (goal) \=\> new Promise((resolve) \=\> {  
    // ... mock logic ...  
});

// \--- AFTER \---  
const runSecurityManager \= async (goal) \=\> {  
    console.log(\`\[Manager\] Sending goal to agent: "${goal}"\`);  
    updateAgentStatus('manager', 'running', 'Translating goal into a tactical plan...');

    const response \= await fetch('YOUR\_API\_ENDPOINT/run-security-manager', {  
        method: 'POST',  
        headers: { 'Content-Type': 'application/json' },  
        body: JSON.stringify({ strategicGoal: goal })  
    });

    if (\!response.ok) {  
        throw new Error('Security Manager Agent failed');  
    }

    const data \= await response.json();  
    const plan \= data.tacticalPlan;

    console.log(\`\[Manager\] Received plan: "${plan}"\`);  
    updateAgentStatus('manager', 'completed', 'Tactical plan created.');  
    return plan;  
};

3. **Deploy Changes:** Upload your modified index.html file to your hosting provider.

Your application should now be fully functional, orchestrating your team of AI agents to perform a complete, automated security audit.