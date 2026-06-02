# AI Project Manager MCP Server

A local **Model Context Protocol (MCP)** server that connects Claude Desktop to a SQLite project management database.

This project demonstrates how an AI assistant can interact with a real backend system through **safe, predefined MCP tools** instead of unrestricted database access. The AI assistant can read project data, update task/risk statuses, generate sprint risk reports, create client-friendly status reports, and record audit logs for traceability.

---

## Overview

The goal of this project is to explore how MCP servers can be used to build practical AI agent workflows.

Instead of building a normal chatbot that only responds with text, this project allows Claude Desktop to perform controlled project management actions through a Python MCP server.

Example:

```text
User prompt:
Generate a sprint risk report.

Claude Desktop:
Calls generate_sprint_risk_report()

MCP Server:
Reads tasks, risks, workload, and overdue items from SQLite

Output:
Structured sprint risk report with risk score and recommendations
```

---

## Architecture

```text
Claude Desktop
    ↓
AI Project Manager MCP Server
    ↓
SQLite Database
    ↓
Tasks, Risks, Sprints, Team Members, Audit Logs
```

The MCP server acts as a controlled bridge between the AI assistant and the project management database.

---

## Features

- Python-based MCP server
- SQLite database integration
- Automatic database/table creation
- Seed data for team members, sprints, tasks, and risks
- Task management tools
- Risk management tools
- Sprint risk report generation
- Team workload analysis
- Client-friendly project status reporting
- Audit logs for AI-triggered write actions
- MCP Inspector testing support
- Claude Desktop local MCP integration

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Protocol | Model Context Protocol |
| MCP Framework | FastMCP / MCP Python SDK |
| Database | SQLite |
| AI Client | Claude Desktop |
| Testing Tool | MCP Inspector |

---

## Project Structure

```text
ai-project-manager-mcp-server/
│
├── server.py              # Main MCP server and tool definitions
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
└── project_manager.db     # Auto-created after first run
```

> `project_manager.db` and the virtual environment should not be committed to GitHub. The database is generated automatically when the server runs.

---

## Database Tables

The SQLite database contains the following tables:

| Table | Purpose |
|---|---|
| `team_members` | Stores project team members and roles |
| `sprints` | Stores sprint names, dates, status, and goals |
| `tasks` | Stores project tasks, priorities, statuses, assignees, and deadlines |
| `risks` | Stores project risks, probability, impact, status, and mitigation plans |
| `audit_logs` | Tracks AI-triggered create/update actions |

---

## MCP Tools

### 1. `get_database_path()`

Returns the database path and server path currently used by the MCP server.

Useful for debugging Claude Desktop path issues.

Example prompt:

```text
Use the AI project manager tool and show me the database path.
```

---

### 2. `get_project_summary()`

Returns a high-level project summary including:

- Total tasks
- Task status breakdown
- Total risks
- Risk status breakdown
- Number of overdue tasks

Example prompt:

```text
Show me the project summary.
```

---

### 3. `get_overdue_tasks()`

Returns tasks where the due date has passed and the task is not completed.

Example prompt:

```text
Show me overdue tasks.
```

---

### 4. `get_tasks_by_status(status)`

Returns tasks filtered by status.

Allowed statuses:

```text
todo
in_progress
blocked
completed
```

Example input:

```json
{
  "status": "todo"
}
```

Example prompt:

```text
Show me all todo tasks.
```

---

### 5. `get_team_workload()`

Returns task workload grouped by team member.

Includes:

- Total tasks
- Completed tasks
- Open tasks
- High-priority open tasks

Example prompt:

```text
Which team members are overloaded?
```

---

### 6. `get_high_risk_items()`

Returns open or mitigating risks with high probability or high impact.

Example prompt:

```text
Show me the high-risk project items.
```

---

### 7. `update_task_status(task_id, new_status)`

Updates a task status and records an audit log.

Allowed statuses:

```text
todo
in_progress
blocked
completed
```

Example input:

```json
{
  "task_id": 3,
  "new_status": "completed"
}
```

Example prompt:

```text
Update task ID 3 status to completed.
```

---

### 8. `add_task(...)`

Adds a new task and records an audit log.

Required fields:

- `title`
- `priority`
- `due_date`
- `assignee_id`
- `sprint_id`
- `description`

Allowed priorities:

```text
low
medium
high
critical
```

Example input:

```json
{
  "title": "Prepare LinkedIn project post",
  "priority": "high",
  "due_date": "2026-06-15",
  "assignee_id": 1,
  "sprint_id": 1,
  "description": "Prepare screenshots, GitHub link, and LinkedIn write-up for the MCP project."
}
```

Example prompt:

```text
Add a high-priority task to prepare the LinkedIn project post.
```

---

### 9. `update_risk_status(risk_id, new_status)`

Updates a risk status and records an audit log.

Allowed statuses:

```text
open
mitigating
closed
```

Example input:

```json
{
  "risk_id": 2,
  "new_status": "mitigating"
}
```

Example prompt:

```text
Update risk ID 2 status to mitigating.
```

---

### 10. `add_project_risk(...)`

Adds a new project risk and records an audit log.

Required fields:

- `title`
- `probability`
- `impact`
- `description`
- `mitigation_plan`

Allowed probability and impact values:

```text
low
medium
high
```

Example input:

```json
{
  "title": "Delayed API integration",
  "probability": "medium",
  "impact": "high",
  "description": "The external API integration may take longer than expected.",
  "mitigation_plan": "Prepare a fallback mock API and assign a dedicated developer."
}
```

Example prompt:

```text
Add a new project risk about delayed API integration with medium probability and high impact.
```

---

### 11. `generate_sprint_risk_report()`

Generates a structured sprint risk report using:

- Project summary
- Overdue tasks
- High-risk items
- Team workload
- Overloaded members
- Risk score
- Recommendations

Example prompt:

```text
Generate a sprint risk report.
```

Example output includes:

```text
overall_risk_level
risk_score
summary
overdue_tasks
high_risk_items
overloaded_members
recommendations
```

---

### 12. `generate_client_status_report()`

Generates a client-friendly project status report.

The report includes:

- Project status
- Executive summary
- Task summary
- Key risks
- Overdue tasks
- Next actions

Example prompt:

```text
Generate a client-ready project status report.
```

---

### 13. `get_audit_logs(limit=10)`

Returns the latest audit log entries.

Example input:

```json
{
  "limit": 10
}
```

Example prompt:

```text
Show me the latest 10 audit logs.
```

---

### 14. `get_audit_logs_for_entity(entity_type, entity_id)`

Returns audit logs for a specific task or risk.

Allowed entity types:

```text
task
risk
```

Example input:

```json
{
  "entity_type": "task",
  "entity_id": 3
}
```

Example prompt:

```text
Show me the audit history for task ID 3.
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-project-manager-mcp-server.git
cd ai-project-manager-mcp-server
```

Or if you are working locally before upload:

```bash
cd ~/Desktop/ai-project-manager-mcp-server
```

---

### 2. Create a virtual environment

```bash
python3 -m venv project_mcp
```

---

### 3. Activate the virtual environment

```bash
source project_mcp/bin/activate
```

Your terminal should show something like:

```text
(project_mcp) yoosufahamed@Yoosufs-MacBook-Air ai-project-manager-mcp-server %
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run with MCP Inspector

MCP Inspector is useful for testing MCP tools before connecting to Claude Desktop.

```bash
mcp dev server.py
```

If Inspector tries to use `uv` and fails, manually set:

```text
Transport Type: STDIO
Command: python
Arguments: server.py
```

Then click **Connect**.

---

## Test with MCP Inspector

After connecting, open the **Tools** section and test these tools:

```text
get_database_path
get_project_summary
get_overdue_tasks
get_team_workload
get_high_risk_items
generate_sprint_risk_report
generate_client_status_report
```

For write tools, test:

```text
update_task_status
```

Example input:

```json
{
  "task_id": 3,
  "new_status": "completed"
}
```

Then check:

```text
get_audit_logs
```

Example input:

```json
{
  "limit": 10
}
```

---

## Connect to Claude Desktop

Claude Desktop can run local MCP servers through its config file.

### 1. Get your Python path

Inside the activated virtual environment:

```bash
which python
```

Example output:

```text
/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/project_mcp/bin/python
```

---

### 2. Get your project path

```bash
pwd
```

Example output:

```text
/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server
```

Your `server.py` path will be:

```text
/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/server.py
```

---

### 3. Open Claude Desktop config

On macOS:

```bash
open -a TextEdit "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

---

### 4. Add MCP server configuration

If your config file already has other MCP servers, add this inside the existing `"mcpServers"` object:

```json
"ai-project-manager": {
  "command": "/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/project_mcp/bin/python",
  "args": [
    "/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/server.py"
  ]
}
```

Full example with multiple MCP servers:

```json
{
  "mcpServers": {
    "pharmacy-inventory": {
      "command": "/path/to/pharmacy_mcp/bin/python",
      "args": [
        "/path/to/pharmacy/server.py"
      ]
    },
    "ai-project-manager": {
      "command": "/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/project_mcp/bin/python",
      "args": [
        "/Users/yoosufahamed/Desktop/ai-project-manager-mcp-server/server.py"
      ]
    }
  }
}
```

Replace the paths with your actual `which python` and `pwd` outputs.

---

### 5. Restart Claude Desktop

Fully quit Claude Desktop:

```text
Command + Q
```

Then reopen Claude Desktop.

---

## Claude Desktop Prompt Examples

Try these prompts after connecting the MCP server.

### Project summary

```text
Use the AI project manager tool and show me the project summary.
```

---

### Overdue tasks

```text
Show me all overdue tasks using the AI project manager tool.
```

---

### Team workload

```text
Which team members are overloaded?
```

---

### Risk report

```text
Generate a sprint risk report using the AI project manager tool.
```

---

### Update task status

```text
Update task ID 3 status to completed using the AI project manager tool.
```

Claude should ask for approval before running the tool.

---

### Audit logs

```text
Show me the latest 10 audit logs from the AI project manager tool.
```

---

### Client report

```text
Generate a client-ready project status report.
```

---

## View Database Manually

You can inspect the SQLite database manually.

```bash
sqlite3 project_manager.db
```

Show tables:

```sql
.tables
```

View tasks:

```sql
SELECT id, title, status, priority, due_date FROM tasks;
```

View risks:

```sql
SELECT id, title, probability, impact, status FROM risks;
```

View audit logs:

```sql
SELECT id, action, entity_type, entity_id, old_value, new_value, created_at
FROM audit_logs
ORDER BY created_at DESC;
```

Exit SQLite:

```sql
.quit
```

---

## Recommended Demo Workflow

For a short LinkedIn or portfolio demo, use this sequence:

```text
Prompt 1:
Show me the project summary.

Prompt 2:
Generate a sprint risk report.

Prompt 3:
Update task ID 3 status to completed.

Prompt 4:
Show me the latest audit logs.

Prompt 5:
Generate a client-ready project status report.
```

This demonstrates:

- AI tool calling
- Database reading
- Controlled database update
- Audit logging
- Risk analysis
- Business-friendly reporting

---

## Security Notes

This project is for local learning and portfolio demonstration.

For production use, improve it with:

- Authentication
- Role-based access control
- Read-only and write-enabled tool separation
- Stronger input validation
- User confirmation for destructive actions
- Permanent audit log retention
- Secure database credentials
- Production database such as PostgreSQL
- API-level access control
- Deployment security

The safe design principle is:

```text
The AI assistant decides which tool to request.
The MCP server controls what is actually allowed.
```

---

## Future Improvements

Possible upgrades:

- Add delete task/risk tools with confirmation rules
- Add task priority update tool
- Add sprint creation and sprint completion tools
- Add CSV/PDF report export
- Add project dashboard using Streamlit or Django
- Add GitHub Issues integration
- Add Jira-style sprint board
- Add email report generation
- Add role-based permissions
- Add remote MCP server deployment
- Replace SQLite with PostgreSQL
- Add unit tests for MCP tools

---

## Learning Outcomes

This project demonstrates:

- Building a Python MCP server
- Exposing backend functions as AI-callable tools
- Connecting an MCP server to SQLite
- Testing tools with MCP Inspector
- Connecting local MCP servers to Claude Desktop
- Creating AI-triggered write actions safely
- Adding audit logs for traceability
- Generating sprint risk and client status reports

---

## Project Status

Current version:

```text
Local prototype completed
```

Main workflow:

```text
Claude Desktop → MCP Server → SQLite Database → Project Management Actions
```

This project is a practical prototype of an **AI Project Manager Agent** built with MCP.
