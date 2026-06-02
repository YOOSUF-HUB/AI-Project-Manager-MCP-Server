# AI Project Manager MCP Server

A local Model Context Protocol (MCP) server that connects Claude Desktop to a SQLite project management database.

## Features

- Python MCP server
- SQLite database integration
- Task management tools
- Risk management tools
- Sprint risk report generation
- Team workload analysis
- Client-friendly status report generation
- Audit logs for AI-triggered updates
- Claude Desktop integration
- MCP Inspector testing support

## Architecture

```text
Claude Desktop
    ↓
AI Project Manager MCP Server
    ↓
SQLite Database
    ↓
Tasks, Risks, Sprints, Team Members, Audit Logs