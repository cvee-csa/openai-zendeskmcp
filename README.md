# OpenAI Zendesk MCP

A Zendesk-focused Model Context Protocol (MCP) server for helpdesk environments, adapted for OpenAI workflows such as Codex.

## What It Can Do

- Read tickets, comments, and audits
- Read users, groups, ticket fields, views, and ticket metrics
- Search tickets with common helpdesk filters
- Create tickets
- Update tickets
- Reassign tickets
- Add internal notes
- Draft and send public replies
- Search Help Center articles

## Project Layout

- `zendesk_mcp_server/server.py` - FastMCP server and Zendesk API bindings
- `zendesk_mcp_server/__init__.py` - package entrypoint
- `zendesk_mcp_server/__main__.py` - `python -m zendesk_mcp_server` entrypoint
- `pyproject.toml` - project metadata and CLI script
- `.env.example` - required environment variables
- `Dockerfile` - container runtime

## Required Environment Variables

Required:

- `ZENDESK_SUBDOMAIN`

Optional:

- `ZENDESK_EMAIL`
- `ZENDESK_API_TOKEN`
- `ZENDESK_CLIENT_ID`
- `ZENDESK_CLIENT_SECRET`
- `ZENDESK_REDIRECT_URI`
- `ZENDESK_OAUTH_SCOPES`
- `ZENDESK_OAUTH_TOKEN_PATH`
- `ZENDESK_TIMEOUT_SECONDS`
- `ZENDESK_HELP_CENTER_PAGE_SIZE`

Copy the example file and fill in your Zendesk credentials:

```bash
cp .env.example .env
```

## Local Setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -e .
./.venv/bin/python -m zendesk_mcp_server
```

The server loads `.env` from the repository root, so it can still find credentials when launched by an MCP client from outside this directory.

Auth modes:

- Preferred: OAuth with `ZENDESK_CLIENT_ID` and `ZENDESK_CLIENT_SECRET`
- Legacy fallback: API token with `ZENDESK_EMAIL` and `ZENDESK_API_TOKEN`

If both are configured, the server prefers OAuth.

## One-Time OAuth Setup

The MCP tool surface stays the same. If OAuth is configured, the server authenticates with Zendesk OAuth `authorization_code` tokens. If only legacy credentials are configured, it continues using API token auth until you migrate.

1. Create a Zendesk OAuth client in Admin Center.
2. Set the client kind to `Confidential`.
3. Add a redirect URI such as `https://localhost/callback`.
4. Fill in `.env` with your subdomain, client ID, client secret, and redirect URI.
5. Start the MCP server and call `begin_oauth_authorization`.
6. Open the returned `authorization_url` in a browser and approve access.
7. After Zendesk redirects to your `redirect_uri`, copy the `code` and `state` query params from the address bar.
8. Call `complete_oauth_authorization(code=..., state=...)`.

By default, the server stores tokens in `.zendesk_oauth_tokens.json` and refreshes them automatically before expiry or after a `401` response.

## Add To Codex

Register the server as a stdio MCP server:

```bash
codex mcp add zendesk -- /Users/catherinevee/Desktop/git/openai-zendeskmcp/.venv/bin/python -m zendesk_mcp_server
```

You can inspect the configured servers with:

```bash
codex mcp list
codex mcp get zendesk
```

## ChatGPT Note

This repository is an MCP server, which makes it a good fit for MCP-capable OpenAI tooling such as Codex. For ChatGPT-style app integrations, OpenAI's Apps SDK is the relevant integration path; that is a separate app surface built around MCP rather than a direct "drop this local repo into ChatGPT" workflow.

## Main Tools

Queue and ticket tools:

- `get_tickets`
- `search_tickets`
- `get_ticket`
- `get_ticket_comments`
- `get_ticket_audits`
- `get_ticket_metrics`
- `summarize_ticket_history`
- `list_ticket_fields`
- `list_views`
- `get_view_tickets`

Write tools:

- `add_internal_note`
- `draft_public_reply`
- `send_public_reply`
- `create_ticket`
- `update_ticket`
- `reassign_ticket`

People and org tools:

- `get_user`
- `find_user`
- `find_org`
- `list_groups`

KB and workflow tools:

- `search_kb`
- `find_relevant_articles_for_ticket`
- `suggest_next_action`
- `detect_escalation_risk`

## Notes

- `draft_public_reply` is intentionally read-only and does not write to Zendesk.
- `send_public_reply` is separated from internal notes to reduce accidental public responses.
- `search_tickets` supports queue-style filters such as status, priority, assignee, requester, group, tags, and date ranges.
- OAuth setup tools are only needed when you want to use OAuth mode.
- If the refresh token expires or is revoked, run the one-time OAuth setup again.
