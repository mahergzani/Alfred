# **AI-Powered Security Audit Web Application**

This project is a web application that simulates and automates a cybersecurity audit of a GitHub repository using a team of specialized AI agents. The application provides an interface for a "Director of Security" to initiate an audit by providing a repository URL and a high-level strategic goal.

## **The AI Agent Team**

The application orchestrates a workflow between four distinct AI agents, each built with a framework like the Google Agent Development Kit and assigned a specific role in the software security lifecycle.

1. **Security Manager Agent:**  
   * **Input:** Receives the strategic goal from the Director of Security (e.g., "Ensure this API is safe from data breaches before our Q4 launch").  
   * **Responsibility:** Translates the high-level business objective into a concrete and actionable tactical plan for the technical agents.  
   * **Output:** A detailed set of instructions for the Penetration Tester, defining the scope, objectives, and priorities of the security test.  
2. **Penetration Tester Agent:**  
   * **Input:** The tactical plan from the Security Manager and access to the repository's source code.  
   * **Responsibility:** Performs a "white-box" security assessment by analyzing the code for vulnerabilities. This includes Static Application Security Testing (SAST) and Software Composition Analysis (SCA).  
   * **Output:** A technical report listing all identified vulnerabilities, their severity, and direct links to the exact lines of code in the repository where they were found.  
3. **Security Engineer Agent:**  
   * **Input:** The vulnerability report from the Penetration Tester.  
   * **Responsibility:** Triages the vulnerabilities, creates actionable tasks for the development team, and focuses on long-term prevention.  
   * **Output:**  
     * Creates GitHub Issues in the repository for each vulnerability.  
     * Adds automated security scanning to the repository via GitHub Actions (.github/workflows/security-scan.yml) to prevent future vulnerabilities.  
4. **Software Engineer Agent:**  
   * **Input:** The GitHub Issues created by the Security Engineer.  
   * **Responsibility:** Acts as a developer to fix the identified security flaws.  
   * **Output:** Writes the necessary code to remediate the vulnerabilities and creates Pull Requests to merge the fixes into the main branch.

## **Workflow**

1. The user (Director of Security) provides a GitHub repository URL and a strategic goal.  
2. The application "copies" the repository (simulated for this example).  
3. The **Security Manager Agent** receives the goal and creates a tactical plan.  
4. The **Penetration Tester Agent** receives the plan and analyzes the code, producing a vulnerability report.  
5. The **Security Engineer Agent** receives the report, creates GitHub Issues, and adds automation workflows.  
6. The **Software Engineer Agent** receives the issues, writes the code fixes, and creates Pull Requests.  
7. The application presents the final, updated GitHub repository link to the user.