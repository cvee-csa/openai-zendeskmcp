# OpenAI Zendesk MCP

A Zendesk-focused Model Context Protocol (MCP) server for helpdesk workflows, modeled after `reminia/zendesk-mcp-server` and adapted for OpenAI-compatible local MCP usage.

## Included capabilities

- Ticket listing, search, retrieval, comments, audits, and history summaries
- Drafted and direct reply flows
- Ticket creation, update, and reassignment tools
- Typed response models for structured outputs
- Help Center article search and ticket-to-KB suggestion helpers
- Workflow helpers for next-action suggestions and escalation risk detection

## Project layout

- `zendesk_mcp_server/server.py` - FastMCP server and Zendesk API bindings
- `zendesk_mcp_server/__init__.py` - package entrypoint
- `pyproject.toml` - project metadata and CLI script
- `.env.example` - required environment variables
- `Dockerfile` - container runtime

## Setup

### Option 1: uv

```bash
cp .env.example .env
uv venv
uv sync
uv run zendesk
```

### Option 2: venv plus pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
zendesk
```

## MCP client configuration

```json
{
  "mcpServers": {
    "zendesk": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/openai-zendeskmcp",
        "run",
        "zendesk"
      ]
    }
  }
}
```

## Environment variables

### Required

- `ZENDESK_SUBDOMAIN`
- `ZENDESK_EMAIL`
- `ZENDESK_API_TOKEN`

### Optional

- `ZENDESK_TIMEOUT_SECONDS`
- `ZENDESK_HELP_CENTER_PAGE_SIZE`
- `ZENDESK_WRITE_ENABLED`

## Main tools

### Queue and ticket tools

- `get_tickets`
- `search_tickets`
- `get_ticket`
- `get_ticket_comments`
- `get_ticket_audits`
- `summarize_ticket_history`

### Write tools

- `add_internal_note`
- `draft_public_reply`
- `send_public_reply`
- `create_ticket`
- `update_ticket`
- `reassign_ticket`

### People and org tools

- `find_user`
- `find_org`

### KB and workflow tools

- `search_kb`
- `find_relevant_articles_for_ticket`
- `suggest_next_action`
- `detect_escalation_risk`

## Safety notes

- `draft_public_reply` is read-only and does not write to Zendesk.
- Write operations should remain disabled unless `ZENDESK_WRITE_ENABLED=true` is explicitly set.
- `send_public_reply` requires explicit confirmation in production usage.
- Search supports filters such as status, priority, assignee, requester, group, tags, and date ranges.
