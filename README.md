# OpenAI Zendesk MCP

A Zendesk-focused Model Context Protocol (MCP) server for helpdesk environments, modeled after `reminia/zendesk-mcp-server` and adapted for ChatGPT / OpenAI workflows.

## What's included

- Ticket tools for listing, searching, reading, commenting, creating, updating, and reassignment
- Safer write actions split into internal notes, draft replies, and public replies
- Typed response models for predictable structured output
- Help Center article search and ticket-to-KB suggestion helpers
- Ticket audit/history tools for handoffs and QA
- Workflow helpers for next-action suggestions and escalation risk detection

## Project layout

- `zendesk_mcp_server/server.py` — FastMCP server and Zendesk API bindings
- `zendesk_mcp_server/__init__.py` — package entrypoint
- `pyproject.toml` — project metadata and CLI script
- `.env.example` — required environment variables
- `Dockerfile` — container runtime

## Setup

```bash
cp .env.example .env
uv venv
uv sync
uv run zendesk

python -m venv .venv
source .venv/bin/activate
pip install -e .
zendesk

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

Environment variables

Required:

ZENDESK_SUBDOMAIN
ZENDESK_EMAIL
ZENDESK_API_TOKEN

Optional:

ZENDESK_TIMEOUT_SECONDS
ZENDESK_HELP_CENTER_PAGE_SIZE
Main tools
Queue and ticket tools
get_tickets
search_tickets
get_ticket
get_ticket_comments
get_ticket_audits
summarize_ticket_history
Safer write tools
add_internal_note
draft_public_reply
send_public_reply
create_ticket
update_ticket
reassign_ticket
People and org tools
find_user
find_org
KB and workflow tools
search_kb
find_relevant_articles_for_ticket
suggest_next_action
detect_escalation_risk
Notes
draft_public_reply is intentionally read-only. It returns a suggested reply without writing to Zendesk.
send_public_reply is separated from internal notes to reduce accidental public responses.
Search supports common queue filters such as status, priority, assignee, requester, group, tags, and date ranges.