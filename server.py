from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("AI Project Manager MCP Server")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "project_manager.db"


TEAM_MEMBERS = [
    ("Yoosuf Ahamed", "Project Lead", "AI / Backend"),
    ("Aisha Perera", "Developer", "Frontend"),
    ("Naveen Silva", "Developer", "Backend"),
    ("Hafsa Rahman", "QA Engineer", "Testing"),
    ("Dilshan Kumar", "UI/UX Designer", "Design"),
]


SPRINTS = [
    (
        "Sprint 1",
        "2026-06-01",
        "2026-06-14",
        "active",
        "Initial MCP project manager prototype",
    ),
    (
        "Sprint 2",
        "2026-06-15",
        "2026-06-28",
        "planned",
        "Reports, validation, and dashboard integration",
    ),
]


TASKS = [
    (
        "Design database schema",
        "completed",
        "high",
        "2026-06-03",
        1,
        1,
        "Create SQLite schema for tasks, risks, members, and audit logs.",
    ),
    (
        "Build MCP server tools",
        "in_progress",
        "high",
        "2026-06-08",
        1,
        1,
        "Expose project management tools through MCP.",
    ),
    (
        "Create Claude Desktop config guide",
        "todo",
        "medium",
        "2026-06-10",
        1,
        1,
        "Document how to connect the MCP server with Claude Desktop.",
    ),
    (
        "Implement audit logs",
        "todo",
        "high",
        "2026-06-09",
        3,
        1,
        "Track AI-triggered updates to tasks and risks.",
    ),
    (
        "Prepare LinkedIn demo video",
        "todo",
        "medium",
        "2026-06-12",
        1,
        1,
        "Record a short demo showing AI tool calls and status report generation.",
    ),
    (
        "Test sprint summary report",
        "todo",
        "medium",
        "2026-06-11",
        4,
        1,
        "Validate report generation output from MCP tools.",
    ),
    (
        "Design simple dashboard mockup",
        "todo",
        "low",
        "2026-06-18",
        5,
        2,
        "Create basic dashboard concept for future upgrade.",
    ),
]


RISKS = [
    (
        "MCP server path misconfiguration",
        "medium",
        "high",
        "open",
        "Claude may point to an old local project directory.",
        "Use get_database_path tool and update Claude config.",
    ),
    (
        "Untracked AI-triggered updates",
        "high",
        "high",
        "open",
        "Updates made through AI tools may not be traceable.",
        "Add audit logs for every write action.",
    ),
    (
        "Scope creep",
        "medium",
        "medium",
        "open",
        "Adding too many features may delay the portfolio release.",
        "Limit first version to tasks, risks, reports, and audit logs.",
    ),
    (
        "Incomplete validation",
        "medium",
        "medium",
        "open",
        "Invalid task or risk inputs may enter the database.",
        "Add input validation to all write tools.",
    ),
]


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection and return rows as dictionary-like objects."""
    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite3.Row object into a normal Python dictionary."""
    return dict(row)

def create_audit_log(
    connection: sqlite3.Connection,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    details: str | None = None,
    performed_by: str = "Claude Desktop / MCP Client",
) -> None:
    """Insert an audit log entry for important AI-triggered actions."""
    connection.execute(
        """
        INSERT INTO audit_logs (
            action,
            entity_type,
            entity_id,
            old_value,
            new_value,
            details,
            performed_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            action,
            entity_type,
            entity_id,
            old_value,
            new_value,
            details,
            performed_by,
        ),
    )


def init_database() -> None:
    """Create database tables and insert sample project data if empty."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                specialization TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('planned', 'active', 'completed')),
                goal TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('todo', 'in_progress', 'blocked', 'completed')),
                priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                due_date TEXT,
                assignee_id INTEGER,
                sprint_id INTEGER,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignee_id) REFERENCES team_members(id),
                FOREIGN KEY (sprint_id) REFERENCES sprints(id)
            );
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                probability TEXT NOT NULL CHECK(probability IN ('low', 'medium', 'high')),
                impact TEXT NOT NULL CHECK(impact IN ('low', 'medium', 'high')),
                status TEXT NOT NULL CHECK(status IN ('open', 'mitigating', 'closed')),
                description TEXT,
                mitigation_plan TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                details TEXT,
                performed_by TEXT DEFAULT 'Claude Desktop / MCP Client',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        member_count = connection.execute(
            "SELECT COUNT(*) FROM team_members;"
        ).fetchone()[0]

        if member_count == 0:
            connection.executemany(
                """
                INSERT INTO team_members (
                    name,
                    role,
                    specialization
                )
                VALUES (?, ?, ?);
                """,
                TEAM_MEMBERS,
            )

        sprint_count = connection.execute(
            "SELECT COUNT(*) FROM sprints;"
        ).fetchone()[0]

        if sprint_count == 0:
            connection.executemany(
                """
                INSERT INTO sprints (
                    name,
                    start_date,
                    end_date,
                    status,
                    goal
                )
                VALUES (?, ?, ?, ?, ?);
                """,
                SPRINTS,
            )

        task_count = connection.execute(
            "SELECT COUNT(*) FROM tasks;"
        ).fetchone()[0]

        if task_count == 0:
            connection.executemany(
                """
                INSERT INTO tasks (
                    title,
                    status,
                    priority,
                    due_date,
                    assignee_id,
                    sprint_id,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                TASKS,
            )

        risk_count = connection.execute(
            "SELECT COUNT(*) FROM risks;"
        ).fetchone()[0]

        if risk_count == 0:
            connection.executemany(
                """
                INSERT INTO risks (
                    title,
                    probability,
                    impact,
                    status,
                    description,
                    mitigation_plan
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                RISKS,
            )

        connection.commit()


@mcp.tool()
def get_database_path() -> dict[str, str]:
    """Return the SQLite database path used by this MCP server."""
    return {
        "database_path": str(DB_PATH),
        "server_path": str(Path(__file__).resolve()),
    }


@mcp.tool()
def say_hello(name: str = "Yoosuf") -> dict[str, str]:
    """Return a simple greeting to test that the MCP server is working."""
    return {
        "message": f"Hello {name}, your AI Project Manager MCP Server is working!"
    }


init_database()

@mcp.tool()
def get_project_summary() -> dict[str, Any]:
    """Return a high-level project summary with task and risk counts."""
    with get_connection() as connection:
        task_counts = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM tasks
            GROUP BY status;
            """
        ).fetchall()

        risk_counts = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM risks
            GROUP BY status;
            """
        ).fetchall()

        total_tasks = connection.execute(
            "SELECT COUNT(*) FROM tasks;"
        ).fetchone()[0]

        total_risks = connection.execute(
            "SELECT COUNT(*) FROM risks;"
        ).fetchone()[0]

        overdue_tasks = connection.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE due_date < DATE('now')
              AND status != 'completed';
            """
        ).fetchone()[0]

        return {
            "total_tasks": total_tasks,
            "task_status_breakdown": [row_to_dict(row) for row in task_counts],
            "total_risks": total_risks,
            "risk_status_breakdown": [row_to_dict(row) for row in risk_counts],
            "overdue_tasks": overdue_tasks,
        }


@mcp.tool()
def get_overdue_tasks() -> list[dict[str, Any]]:
    """Return tasks that are overdue and not completed."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                tasks.id,
                tasks.title,
                tasks.status,
                tasks.priority,
                tasks.due_date,
                team_members.name AS assignee,
                sprints.name AS sprint
            FROM tasks
            LEFT JOIN team_members ON tasks.assignee_id = team_members.id
            LEFT JOIN sprints ON tasks.sprint_id = sprints.id
            WHERE tasks.due_date < DATE('now')
              AND tasks.status != 'completed'
            ORDER BY tasks.due_date ASC;
            """
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    


@mcp.tool()
def get_team_workload() -> list[dict[str, Any]]:
    """Return task workload grouped by team member."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                team_members.id AS member_id,
                team_members.name,
                team_members.role,
                team_members.specialization,
                COUNT(tasks.id) AS total_tasks,
                SUM(CASE WHEN tasks.status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
                SUM(CASE WHEN tasks.status != 'completed' THEN 1 ELSE 0 END) AS open_tasks,
                SUM(
                    CASE
                        WHEN tasks.priority IN ('high', 'critical')
                         AND tasks.status != 'completed'
                        THEN 1 ELSE 0
                    END
                ) AS high_priority_open_tasks
            FROM team_members
            LEFT JOIN tasks ON team_members.id = tasks.assignee_id
            GROUP BY team_members.id
            ORDER BY open_tasks DESC, high_priority_open_tasks DESC;
            """
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    



@mcp.tool()
def get_high_risk_items() -> list[dict[str, Any]]:
    """Return open or mitigating risks with high probability or high impact."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM risks
            WHERE status != 'closed'
              AND (probability = 'high' OR impact = 'high')
            ORDER BY
                CASE impact
                    WHEN 'high' THEN 3
                    WHEN 'medium' THEN 2
                    ELSE 1
                END DESC,
                CASE probability
                    WHEN 'high' THEN 3
                    WHEN 'medium' THEN 2
                    ELSE 1
                END DESC;
            """
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    

@mcp.tool()
def get_tasks_by_status(status: str) -> list[dict[str, Any]]:
    """Return tasks filtered by status."""
    allowed_statuses = {"todo", "in_progress", "blocked", "completed"}
    status = status.strip().lower()

    if status not in allowed_statuses:
        return [
            {
                "error": (
                    "Invalid status. Use one of: "
                    + ", ".join(sorted(allowed_statuses))
                )
            }
        ]

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                tasks.id,
                tasks.title,
                tasks.status,
                tasks.priority,
                tasks.due_date,
                team_members.name AS assignee,
                sprints.name AS sprint,
                tasks.description
            FROM tasks
            LEFT JOIN team_members ON tasks.assignee_id = team_members.id
            LEFT JOIN sprints ON tasks.sprint_id = sprints.id
            WHERE tasks.status = ?
            ORDER BY tasks.due_date ASC;
            """,
            (status,),
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    

@mcp.tool()
def update_task_status(task_id: int, new_status: str) -> dict[str, Any]:
    """Update a task status and record an audit log."""
    allowed_statuses = {"todo", "in_progress", "blocked", "completed"}
    new_status = new_status.strip().lower()

    if task_id <= 0:
        return {"error": "Task ID must be a positive number."}

    if new_status not in allowed_statuses:
        return {
            "error": (
                "Invalid status. Use one of: "
                + ", ".join(sorted(allowed_statuses))
            )
        }

    with get_connection() as connection:
        task = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = ?;
            """,
            (task_id,),
        ).fetchone()

        if task is None:
            return {"error": f"No task found with ID {task_id}."}

        old_status = task["status"]
        task_title = task["title"]

        connection.execute(
            """
            UPDATE tasks
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (new_status, task_id),
        )

        create_audit_log(
            connection=connection,
            action="UPDATE_TASK_STATUS",
            entity_type="task",
            entity_id=task_id,
            old_value=old_status,
            new_value=new_status,
            details=f"Task '{task_title}' status changed from {old_status} to {new_status}.",
        )

        connection.commit()

        updated_task = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = ?;
            """,
            (task_id,),
        ).fetchone()

        return {
            "message": "Task status updated successfully and audit log recorded.",
            "task": row_to_dict(updated_task),
            "audit": {
                "action": "UPDATE_TASK_STATUS",
                "entity_type": "task",
                "entity_id": task_id,
                "old_value": old_status,
                "new_value": new_status,
            },
        }
    
@mcp.tool()
def add_task(
    title: str,
    priority: str,
    due_date: str,
    assignee_id: int,
    sprint_id: int,
    description: str = "",
) -> dict[str, Any]:
    """Add a new project task and record an audit log."""
    allowed_priorities = {"low", "medium", "high", "critical"}

    title = title.strip()
    priority = priority.strip().lower()
    description = description.strip()

    if not title:
        return {"error": "Task title cannot be empty."}

    if priority not in allowed_priorities:
        return {
            "error": (
                "Invalid priority. Use one of: "
                + ", ".join(sorted(allowed_priorities))
            )
        }

    if assignee_id <= 0:
        return {"error": "Assignee ID must be a positive number."}

    if sprint_id <= 0:
        return {"error": "Sprint ID must be a positive number."}

    with get_connection() as connection:
        assignee = connection.execute(
            """
            SELECT id
            FROM team_members
            WHERE id = ?;
            """,
            (assignee_id,),
        ).fetchone()

        if assignee is None:
            return {"error": f"No team member found with ID {assignee_id}."}

        sprint = connection.execute(
            """
            SELECT id
            FROM sprints
            WHERE id = ?;
            """,
            (sprint_id,),
        ).fetchone()

        if sprint is None:
            return {"error": f"No sprint found with ID {sprint_id}."}

        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                status,
                priority,
                due_date,
                assignee_id,
                sprint_id,
                description
            )
            VALUES (?, 'todo', ?, ?, ?, ?, ?);
            """,
            (
                title,
                priority,
                due_date,
                assignee_id,
                sprint_id,
                description,
            ),
        )

        task_id = cursor.lastrowid

        create_audit_log(
            connection=connection,
            action="ADD_TASK",
            entity_type="task",
            entity_id=task_id,
            old_value=None,
            new_value="todo",
            details=f"New task '{title}' added with priority {priority}.",
        )

        connection.commit()

        new_task = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = ?;
            """,
            (task_id,),
        ).fetchone()

        return {
            "message": "Task added successfully and audit log recorded.",
            "task": row_to_dict(new_task),
            "audit": {
                "action": "ADD_TASK",
                "entity_type": "task",
                "entity_id": task_id,
            },
        }
    

@mcp.tool()
def update_risk_status(risk_id: int, new_status: str) -> dict[str, Any]:
    """Update a risk status and record an audit log."""
    allowed_statuses = {"open", "mitigating", "closed"}
    new_status = new_status.strip().lower()

    if risk_id <= 0:
        return {"error": "Risk ID must be a positive number."}

    if new_status not in allowed_statuses:
        return {
            "error": (
                "Invalid status. Use one of: "
                + ", ".join(sorted(allowed_statuses))
            )
        }

    with get_connection() as connection:
        risk = connection.execute(
            """
            SELECT *
            FROM risks
            WHERE id = ?;
            """,
            (risk_id,),
        ).fetchone()

        if risk is None:
            return {"error": f"No risk found with ID {risk_id}."}

        old_status = risk["status"]
        risk_title = risk["title"]

        connection.execute(
            """
            UPDATE risks
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (new_status, risk_id),
        )

        create_audit_log(
            connection=connection,
            action="UPDATE_RISK_STATUS",
            entity_type="risk",
            entity_id=risk_id,
            old_value=old_status,
            new_value=new_status,
            details=f"Risk '{risk_title}' status changed from {old_status} to {new_status}.",
        )

        connection.commit()

        updated_risk = connection.execute(
            """
            SELECT *
            FROM risks
            WHERE id = ?;
            """,
            (risk_id,),
        ).fetchone()

        return {
            "message": "Risk status updated successfully and audit log recorded.",
            "risk": row_to_dict(updated_risk),
            "audit": {
                "action": "UPDATE_RISK_STATUS",
                "entity_type": "risk",
                "entity_id": risk_id,
                "old_value": old_status,
                "new_value": new_status,
            },
        }
    

@mcp.tool()
def add_project_risk(
    title: str,
    probability: str,
    impact: str,
    description: str,
    mitigation_plan: str,
) -> dict[str, Any]:
    """Add a new project risk and record an audit log."""
    allowed_levels = {"low", "medium", "high"}

    title = title.strip()
    probability = probability.strip().lower()
    impact = impact.strip().lower()
    description = description.strip()
    mitigation_plan = mitigation_plan.strip()

    if not title:
        return {"error": "Risk title cannot be empty."}

    if probability not in allowed_levels:
        return {"error": "Probability must be low, medium, or high."}

    if impact not in allowed_levels:
        return {"error": "Impact must be low, medium, or high."}

    if not description:
        return {"error": "Risk description cannot be empty."}

    if not mitigation_plan:
        return {"error": "Mitigation plan cannot be empty."}

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO risks (
                title,
                probability,
                impact,
                status,
                description,
                mitigation_plan
            )
            VALUES (?, ?, ?, 'open', ?, ?);
            """,
            (
                title,
                probability,
                impact,
                description,
                mitigation_plan,
            ),
        )

        risk_id = cursor.lastrowid

        create_audit_log(
            connection=connection,
            action="ADD_RISK",
            entity_type="risk",
            entity_id=risk_id,
            old_value=None,
            new_value="open",
            details=(
                f"New risk '{title}' added with "
                f"{probability} probability and {impact} impact."
            ),
        )

        connection.commit()

        new_risk = connection.execute(
            """
            SELECT *
            FROM risks
            WHERE id = ?;
            """,
            (risk_id,),
        ).fetchone()

        return {
            "message": "Risk added successfully and audit log recorded.",
            "risk": row_to_dict(new_risk),
            "audit": {
                "action": "ADD_RISK",
                "entity_type": "risk",
                "entity_id": risk_id,
            },
        }
    

@mcp.tool()
def get_audit_logs(limit: int = 10) -> list[dict[str, Any]]:
    """Return the latest audit log entries."""
    if limit <= 0:
        limit = 10

    if limit > 100:
        limit = 100

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM audit_logs
            ORDER BY created_at DESC, id DESC
            LIMIT ?;
            """,
            (limit,),
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    

@mcp.tool()
def get_audit_logs_for_entity(
    entity_type: str,
    entity_id: int,
) -> list[dict[str, Any]]:
    """Return audit logs for a specific task or risk."""
    entity_type = entity_type.strip().lower()

    if entity_type not in {"task", "risk"}:
        return [{"error": "Entity type must be either 'task' or 'risk'."}]

    if entity_id <= 0:
        return [{"error": "Entity ID must be a positive number."}]

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM audit_logs
            WHERE entity_type = ?
              AND entity_id = ?
            ORDER BY created_at DESC, id DESC;
            """,
            (entity_type, entity_id),
        ).fetchall()

        return [row_to_dict(row) for row in rows]
    

@mcp.tool()
def generate_sprint_risk_report() -> dict[str, Any]:
    """Generate a structured sprint risk report using project data."""
    summary = get_project_summary()
    overdue_tasks = get_overdue_tasks()
    high_risks = get_high_risk_items()
    workload = get_team_workload()

    overloaded_members = [
        member
        for member in workload
        if member["open_tasks"] is not None and member["open_tasks"] >= 3
    ]

    risk_score = 0
    risk_score += len(overdue_tasks) * 2
    risk_score += len(high_risks) * 3
    risk_score += len(overloaded_members) * 2

    if risk_score >= 10:
        overall_risk_level = "high"
    elif risk_score >= 5:
        overall_risk_level = "medium"
    else:
        overall_risk_level = "low"

    return {
        "report_type": "Sprint Risk Report",
        "overall_risk_level": overall_risk_level,
        "risk_score": risk_score,
        "risk_score_formula": {
            "overdue_task_weight": "2 points each",
            "high_risk_item_weight": "3 points each",
            "overloaded_member_weight": "2 points each",
        },
        "summary": summary,
        "overdue_tasks": overdue_tasks,
        "high_risk_items": high_risks,
        "overloaded_members": overloaded_members,
        "recommendations": [
            "Prioritize overdue high-priority tasks before starting new work.",
            "Assign mitigation owners for all high-impact risks.",
            "Reduce workload imbalance before the next sprint review.",
            "Review audit logs to track AI-triggered project updates.",
        ],
    }

@mcp.tool()
def generate_client_status_report() -> dict[str, Any]:
    """Generate a client-friendly project status report."""
    summary = get_project_summary()
    high_risks = get_high_risk_items()
    overdue_tasks = get_overdue_tasks()

    if summary["overdue_tasks"] > 2 or len(high_risks) >= 2:
        project_status = "At Risk"
    elif summary["overdue_tasks"] > 0 or len(high_risks) == 1:
        project_status = "Needs Attention"
    else:
        project_status = "On Track"

    executive_summary = (
        f"The project is currently marked as '{project_status}'. "
        f"There are {summary['total_tasks']} total tasks, "
        f"{summary['overdue_tasks']} overdue tasks, and "
        f"{len(high_risks)} high-priority risk items requiring attention."
    )

    return {
        "report_type": "Client Status Report",
        "project_status": project_status,
        "executive_summary": executive_summary,
        "task_summary": summary["task_status_breakdown"],
        "key_risks": high_risks,
        "overdue_tasks": overdue_tasks,
        "next_actions": [
            "Review overdue tasks and assign clear owners.",
            "Update mitigation plans for high-impact risks.",
            "Prepare sprint review notes based on current status.",
            "Confirm whether the current sprint scope should be adjusted.",
        ],
    }






if __name__ == "__main__":
    mcp.run()