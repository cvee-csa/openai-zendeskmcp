import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

mcp = FastMCP("Zendesk MCP Server", json_response=True)

SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN", "").strip()
EMAIL = os.getenv("ZENDESK_EMAIL", "").strip()
TOKEN = os.getenv("ZENDESK_API_TOKEN", "").strip()
TIMEOUT = int(os.getenv("ZENDESK_TIMEOUT_SECONDS", "30"))
HELP_CENTER_PAGE_SIZE = int(os.getenv("ZENDESK_HELP_CENTER_PAGE_SIZE", "25"))

if not SUBDOMAIN:
    BASE_URL = ""
else:
    BASE_URL = f"https://{SUBDOMAIN}.zendesk.com/api/v2"

VALID_STATUSES = {"new", "open", "pending", "hold", "solved", "closed"}
VALID_PRIORITIES = {"low", "normal", "high", "urgent"}
VALID_TICKET_TYPES = {"problem", "incident", "question", "task"}


class TicketSummary(BaseModel):
    id: int
    subject: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    assignee_id: Optional[int] = None
    requester_id: Optional[int] = None
    organization_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    url: Optional[str] = None


class TicketListResponse(BaseModel):
    tickets: List[TicketSummary]
    count: int
    query: Optional[str] = None


class TicketDetailResponse(BaseModel):
    id: int
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    assignee_id: Optional[int] = None
    requester_id: Optional[int] = None
    organization_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    due_at: Optional[str] = None
    via_channel: Optional[str] = None
    url: Optional[str] = None


class CommentModel(BaseModel):
    id: int
    author_id: Optional[int] = None
    body: str
    public: bool
    created_at: Optional[str] = None


class TicketCommentsResponse(BaseModel):
    ticket_id: int
    comments: List[CommentModel]


class AuditEventModel(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    field_name: Optional[str] = None
    value: Optional[Any] = None
    body: Optional[str] = None
    public: Optional[bool] = None


class AuditModel(BaseModel):
    id: int
    author_id: Optional[int] = None
    created_at: Optional[str] = None
    events: List[AuditEventModel] = Field(default_factory=list)


class TicketAuditsResponse(BaseModel):
    ticket_id: int
    audits: List[AuditModel]


class MutationResponse(BaseModel):
    success: bool
    ticket_id: Optional[int] = None
    message: Optional[str] = None


class UserSummary(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[int] = None
    role: Optional[str] = None
    suspended: Optional[bool] = None


class UserSearchResponse(BaseModel):
    users: List[UserSummary]
    count: int
    query: Optional[str] = None


class OrganizationSummary(BaseModel):
    id: int
    name: Optional[str] = None
    shared_tickets: Optional[bool] = None
    shared_comments: Optional[bool] = None
    details: Optional[str] = None
    notes: Optional[str] = None


class OrganizationSearchResponse(BaseModel):
    organizations: List[OrganizationSummary]
    count: int
    query: Optional[str] = None


class UserDetailResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[int] = None
    role: Optional[str] = None
    suspended: Optional[bool] = None
    details: Optional[str] = None
    notes: Optional[str] = None
    time_zone: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GroupSummary(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    deleted: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GroupListResponse(BaseModel):
    groups: List[GroupSummary]
    count: int


class TicketFieldOption(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None


class TicketFieldSummary(BaseModel):
    id: int
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None
    active: Optional[bool] = None
    visible_in_portal: Optional[bool] = None
    custom_field_options: List[TicketFieldOption] = Field(default_factory=list)


class TicketFieldListResponse(BaseModel):
    ticket_fields: List[TicketFieldSummary]
    count: int


class ArticleSummary(BaseModel):
    id: int
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None
    section_id: Optional[int] = None
    category_id: Optional[int] = None
    locale: Optional[str] = None
    label_names: List[str] = Field(default_factory=list)


class KBSearchResponse(BaseModel):
    articles: List[ArticleSummary]
    count: int
    query: Optional[str] = None


class ReplyDraftResponse(BaseModel):
    ticket_id: int
    draft_reply: str


class TicketHistorySummaryResponse(BaseModel):
    ticket_id: int
    summary: str


class NextActionResponse(BaseModel):
    ticket_id: int
    recommendation: str
    rationale: List[str] = Field(default_factory=list)


class EscalationRiskResponse(BaseModel):
    ticket_id: int
    risk_level: Literal["low", "medium", "high"]
    signals: List[str] = Field(default_factory=list)


class ViewSummary(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    active: Optional[bool] = None
    execution: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ViewListResponse(BaseModel):
    views: List[ViewSummary]
    count: int


class TicketMetricsResponse(BaseModel):
    ticket_id: int
    reply_time_in_minutes: Optional[Dict[str, Any]] = None
    full_resolution_time_in_minutes: Optional[Dict[str, Any]] = None
    agent_wait_time_in_minutes: Optional[Dict[str, Any]] = None
    requester_wait_time_in_minutes: Optional[Dict[str, Any]] = None
    on_hold_time_in_minutes: Optional[Dict[str, Any]] = None
    group_stations: Optional[int] = None
    assignee_stations: Optional[int] = None
    reopens: Optional[int] = None
    replies: Optional[int] = None
    assignee_updated_at: Optional[str] = None
    requester_updated_at: Optional[str] = None
    status_updated_at: Optional[str] = None
    initially_assigned_at: Optional[str] = None
    assigned_at: Optional[str] = None
    solved_at: Optional[str] = None
    latest_comment_added_at: Optional[str] = None


def _clean_text(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty.")
    return cleaned


def _validate_choice(
    value: Optional[str],
    *,
    field_name: str,
    allowed: set[str],
) -> Optional[str]:
    if value is None:
        return None
    normalized = _clean_text(value, field_name=field_name).lower()
    if normalized not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{field_name} must be one of: {allowed_values}.")
    return normalized


def _normalize_tags(tags: Optional[List[str]]) -> Optional[List[str]]:
    if tags is None:
        return None
    normalized = [_clean_text(tag, field_name="tag") for tag in tags]
    if len(set(normalized)) != len(normalized):
        raise ValueError("tags must not contain duplicates.")
    return normalized


def _extract_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        error = payload.get("error")
        description = payload.get("description")
        details = payload.get("details")
        parts = [str(part) for part in (error, description, details) if part]
        if parts:
            return " - ".join(parts)
    return response.text.strip() or "Zendesk returned an error without a response body."


def _require_config() -> None:
    missing = []
    if not SUBDOMAIN:
        missing.append("ZENDESK_SUBDOMAIN")
    if not EMAIL:
        missing.append("ZENDESK_EMAIL")
    if not TOKEN:
        missing.append("ZENDESK_API_TOKEN")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def _auth() -> tuple[str, str]:
    return (f"{EMAIL}/token", TOKEN)


def _zd_request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    _require_config()
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            params=params,
            json=json,
            auth=_auth(),
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        message = _extract_error_message(exc.response) if exc.response is not None else str(exc)
        raise RuntimeError(f"Zendesk API request failed ({status_code}): {message}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Zendesk API request failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("Zendesk returned a non-JSON response.") from exc


def _ticket_summary(ticket: Dict[str, Any]) -> TicketSummary:
    return TicketSummary(
        id=ticket["id"],
        subject=ticket.get("subject"),
        status=ticket.get("status"),
        priority=ticket.get("priority"),
        type=ticket.get("type"),
        assignee_id=ticket.get("assignee_id"),
        requester_id=ticket.get("requester_id"),
        organization_id=ticket.get("organization_id"),
        tags=ticket.get("tags") or [],
        created_at=ticket.get("created_at"),
        updated_at=ticket.get("updated_at"),
        url=ticket.get("url"),
    )


def _ticket_detail(ticket: Dict[str, Any]) -> TicketDetailResponse:
    via = ticket.get("via") or {}
    return TicketDetailResponse(
        id=ticket["id"],
        subject=ticket.get("subject"),
        description=ticket.get("description"),
        status=ticket.get("status"),
        priority=ticket.get("priority"),
        type=ticket.get("type"),
        assignee_id=ticket.get("assignee_id"),
        requester_id=ticket.get("requester_id"),
        organization_id=ticket.get("organization_id"),
        tags=ticket.get("tags") or [],
        created_at=ticket.get("created_at"),
        updated_at=ticket.get("updated_at"),
        due_at=ticket.get("due_at"),
        via_channel=via.get("channel"),
        url=ticket.get("url"),
    )


def _comment_model(comment: Dict[str, Any]) -> CommentModel:
    return CommentModel(
        id=comment["id"],
        author_id=comment.get("author_id"),
        body=comment.get("body") or "",
        public=bool(comment.get("public")),
        created_at=comment.get("created_at"),
    )


def _article_summary(article: Dict[str, Any]) -> ArticleSummary:
    return ArticleSummary(
        id=article["id"],
        title=article.get("title"),
        body=article.get("body"),
        url=article.get("html_url") or article.get("url"),
        section_id=article.get("section_id"),
        category_id=article.get("category_id"),
        locale=article.get("locale"),
        label_names=article.get("label_names") or [],
    )


def _user_summary(user: Dict[str, Any]) -> UserSummary:
    return UserSummary(
        id=user["id"],
        name=user.get("name"),
        email=user.get("email"),
        organization_id=user.get("organization_id"),
        role=user.get("role"),
        suspended=user.get("suspended"),
    )


def _user_detail(user: Dict[str, Any]) -> UserDetailResponse:
    return UserDetailResponse(
        id=user["id"],
        name=user.get("name"),
        email=user.get("email"),
        organization_id=user.get("organization_id"),
        role=user.get("role"),
        suspended=user.get("suspended"),
        details=user.get("details"),
        notes=user.get("notes"),
        time_zone=user.get("time_zone"),
        created_at=user.get("created_at"),
        updated_at=user.get("updated_at"),
    )


def _group_summary(group: Dict[str, Any]) -> GroupSummary:
    return GroupSummary(
        id=group["id"],
        name=group.get("name"),
        description=group.get("description"),
        is_default=group.get("is_default"),
        deleted=group.get("deleted"),
        created_at=group.get("created_at"),
        updated_at=group.get("updated_at"),
    )


def _ticket_field_summary(ticket_field: Dict[str, Any]) -> TicketFieldSummary:
    options = [
        TicketFieldOption(name=option.get("name"), value=option.get("value"))
        for option in ticket_field.get("custom_field_options", [])
    ]
    return TicketFieldSummary(
        id=ticket_field["id"],
        title=ticket_field.get("title"),
        type=ticket_field.get("type"),
        description=ticket_field.get("description"),
        required=ticket_field.get("required"),
        active=ticket_field.get("active"),
        visible_in_portal=ticket_field.get("visible_in_portal"),
        custom_field_options=options,
    )


def _view_summary(view: Dict[str, Any]) -> ViewSummary:
    return ViewSummary(
        id=view["id"],
        title=view.get("title"),
        description=view.get("description"),
        position=view.get("position"),
        active=view.get("active"),
        execution=view.get("execution"),
        created_at=view.get("created_at"),
        updated_at=view.get("updated_at"),
    )


def _build_search_query(
    *,
    query: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    requester: Optional[str] = None,
    group: Optional[str] = None,
    tags: Optional[List[str]] = None,
    created_since: Optional[str] = None,
    updated_since: Optional[str] = None,
) -> str:
    parts: List[str] = ["type:ticket"]
    if query:
        parts.append(query)
    if status:
        parts.append(f"status:{status}")
    if priority:
        parts.append(f"priority:{priority}")
    if assignee:
        parts.append(f"assignee:{assignee}")
    if requester:
        parts.append(f"requester:{requester}")
    if group:
        parts.append(f"group:{group}")
    if tags:
        for tag in tags:
            parts.append(f"tags:{tag}")
    if created_since:
        parts.append(f'created>{created_since}')
    if updated_since:
        parts.append(f'updated>{updated_since}')
    return " ".join(parts)


@mcp.tool()
def get_tickets(
    page: int = 1,
    per_page: int = 25,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Dict[str, Any]:
    """List Zendesk tickets."""
    per_page = max(1, min(per_page, 100))
    data = _zd_request(
        "GET",
        "/tickets.json",
        params={
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
    )
    tickets = [_ticket_summary(t) for t in data.get("tickets", [])]
    return TicketListResponse(tickets=tickets, count=len(tickets)).model_dump()


@mcp.tool()
def search_tickets(
    query: str = "",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    requester: Optional[str] = None,
    group: Optional[str] = None,
    tags: Optional[List[str]] = None,
    created_since: Optional[str] = None,
    updated_since: Optional[str] = None,
    page: int = 1,
) -> Dict[str, Any]:
    """Search tickets using Zendesk search syntax with helpdesk-oriented filters."""
    q = _build_search_query(
        query=query,
        status=status,
        priority=priority,
        assignee=assignee,
        requester=requester,
        group=group,
        tags=tags,
        created_since=created_since,
        updated_since=updated_since,
    )
    data = _zd_request("GET", "/search.json", params={"query": q, "page": page})
    tickets = [
        _ticket_summary(result)
        for result in data.get("results", [])
        if result.get("result_type") == "ticket"
    ]
    return TicketListResponse(tickets=tickets, count=len(tickets), query=q).model_dump()


@mcp.tool()
def get_ticket(ticket_id: int) -> Dict[str, Any]:
    """Fetch a single Zendesk ticket."""
    data = _zd_request("GET", f"/tickets/{ticket_id}.json")
    return _ticket_detail(data["ticket"]).model_dump()


@mcp.tool()
def get_ticket_comments(ticket_id: int) -> Dict[str, Any]:
    """Fetch comments for a ticket."""
    data = _zd_request("GET", f"/tickets/{ticket_id}/comments.json")
    comments = [_comment_model(c) for c in data.get("comments", [])]
    return TicketCommentsResponse(ticket_id=ticket_id, comments=comments).model_dump()


@mcp.tool()
def get_ticket_audits(ticket_id: int) -> Dict[str, Any]:
    """Fetch ticket audits for handoffs and QA."""
    data = _zd_request("GET", f"/tickets/{ticket_id}/audits.json")
    audits: List[AuditModel] = []
    for audit in data.get("audits", []):
        events = []
        for event in audit.get("events", []):
            events.append(
                AuditEventModel(
                    id=event.get("id"),
                    type=event.get("type"),
                    field_name=event.get("field_name"),
                    value=event.get("value"),
                    body=event.get("body"),
                    public=event.get("public"),
                )
            )
        audits.append(
            AuditModel(
                id=audit["id"],
                author_id=audit.get("author_id"),
                created_at=audit.get("created_at"),
                events=events,
            )
        )
    return TicketAuditsResponse(ticket_id=ticket_id, audits=audits).model_dump()


@mcp.tool()
def summarize_ticket_history(ticket_id: int) -> Dict[str, Any]:
    """Summarize the ticket audit trail into a short handoff-friendly narrative."""
    audits_data = get_ticket_audits(ticket_id)
    audits = audits_data["audits"]

    if not audits:
        summary = "No audit history found for this ticket."
        return TicketHistorySummaryResponse(ticket_id=ticket_id, summary=summary).model_dump()

    lines: List[str] = []
    for audit in audits[-10:]:
        created_at = audit.get("created_at") or "unknown time"
        event_bits: List[str] = []
        for event in audit.get("events", []):
            event_type = event.get("type")
            if event_type == "Comment" and event.get("body"):
                visibility = "public reply" if event.get("public") else "internal note"
                event_bits.append(f"{visibility} added")
            elif event_type == "Change":
                field_name = event.get("field_name") or "field"
                value = event.get("value")
                event_bits.append(f"{field_name} changed to {value}")
        if event_bits:
            lines.append(f"- {created_at}: " + "; ".join(event_bits))

    summary = "\n".join(lines) if lines else "Audit history exists, but no summary-worthy events were found."
    return TicketHistorySummaryResponse(ticket_id=ticket_id, summary=summary).model_dump()


@mcp.tool()
def add_internal_note(ticket_id: int, note: str) -> Dict[str, Any]:
    """Add a private internal note to a ticket."""
    note = _clean_text(note, field_name="note")
    _zd_request(
        "PUT",
        f"/tickets/{ticket_id}.json",
        json={"ticket": {"comment": {"body": note, "public": False}}},
    )
    return MutationResponse(success=True, ticket_id=ticket_id, message="Internal note added.").model_dump()


@mcp.tool()
def draft_public_reply(ticket_id: int) -> Dict[str, Any]:
    """Draft a reply without writing to Zendesk."""
    ticket = get_ticket(ticket_id)
    comments = get_ticket_comments(ticket_id)
    description = ticket.get("description") or ""
    latest_comment = comments["comments"][-1]["body"] if comments["comments"] else description

    draft = (
        "Hi,\n\n"
        "Thanks for reaching out. I reviewed your request and we're looking into it.\n\n"
        f"Summary of the latest issue reported:\n{latest_comment[:800]}\n\n"
        "Next steps:\n"
        "- We are reviewing the details provided\n"
        "- We'll follow up if we need additional information\n"
        "- We'll update you as soon as we have a resolution or workaround\n\n"
        "Best,\nSupport"
    )
    return ReplyDraftResponse(ticket_id=ticket_id, draft_reply=draft).model_dump()


@mcp.tool()
def send_public_reply(ticket_id: int, reply: str) -> Dict[str, Any]:
    """Send a public reply to a ticket."""
    reply = _clean_text(reply, field_name="reply")
    _zd_request(
        "PUT",
        f"/tickets/{ticket_id}.json",
        json={"ticket": {"comment": {"body": reply, "public": True}}},
    )
    return MutationResponse(success=True, ticket_id=ticket_id, message="Public reply sent.").model_dump()


@mcp.tool()
def create_ticket(
    subject: str,
    description: str,
    requester_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    priority: Optional[str] = None,
    ticket_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Create a Zendesk ticket."""
    subject = _clean_text(subject, field_name="subject")
    description = _clean_text(description, field_name="description")
    priority = _validate_choice(priority, field_name="priority", allowed=VALID_PRIORITIES)
    ticket_type = _validate_choice(ticket_type, field_name="ticket_type", allowed=VALID_TICKET_TYPES)
    tags = _normalize_tags(tags)

    ticket: Dict[str, Any] = {
        "subject": subject,
        "comment": {"body": description},
    }
    if requester_id is not None:
        ticket["requester_id"] = requester_id
    if assignee_id is not None:
        ticket["assignee_id"] = assignee_id
    if priority:
        ticket["priority"] = priority
    if ticket_type:
        ticket["type"] = ticket_type
    if tags:
        ticket["tags"] = tags
    if custom_fields:
        ticket["custom_fields"] = custom_fields

    data = _zd_request("POST", "/tickets.json", json={"ticket": ticket})
    return MutationResponse(
        success=True,
        ticket_id=data["ticket"]["id"],
        message="Ticket created.",
    ).model_dump()


@mcp.tool()
def update_ticket(
    ticket_id: int,
    subject: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    requester_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[List[Dict[str, Any]]] = None,
    due_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Update writable ticket fields."""
    ticket: Dict[str, Any] = {}
    if subject is not None:
        ticket["subject"] = _clean_text(subject, field_name="subject")
    if status is not None:
        ticket["status"] = _validate_choice(status, field_name="status", allowed=VALID_STATUSES)
    if priority is not None:
        ticket["priority"] = _validate_choice(priority, field_name="priority", allowed=VALID_PRIORITIES)
    if ticket_type is not None:
        ticket["type"] = _validate_choice(ticket_type, field_name="ticket_type", allowed=VALID_TICKET_TYPES)
    if assignee_id is not None:
        ticket["assignee_id"] = assignee_id
    if requester_id is not None:
        ticket["requester_id"] = requester_id
    if tags is not None:
        ticket["tags"] = _normalize_tags(tags)
    if custom_fields is not None:
        ticket["custom_fields"] = custom_fields
    if due_at is not None:
        ticket["due_at"] = _clean_text(due_at, field_name="due_at")

    if not ticket:
        raise ValueError("update_ticket requires at least one field to update.")

    _zd_request("PUT", f"/tickets/{ticket_id}.json", json={"ticket": ticket})
    return MutationResponse(success=True, ticket_id=ticket_id, message="Ticket updated.").model_dump()


@mcp.tool()
def reassign_ticket(ticket_id: int, assignee_id: int) -> Dict[str, Any]:
    """Reassign a ticket to another agent."""
    _zd_request(
        "PUT",
        f"/tickets/{ticket_id}.json",
        json={"ticket": {"assignee_id": assignee_id}},
    )
    return MutationResponse(success=True, ticket_id=ticket_id, message="Ticket reassigned.").model_dump()


@mcp.tool()
def get_user(user_id: int) -> Dict[str, Any]:
    """Fetch a single Zendesk user by ID."""
    data = _zd_request("GET", f"/users/{user_id}.json")
    return _user_detail(data["user"]).model_dump()


@mcp.tool()
def find_user(query: str) -> Dict[str, Any]:
    """Find Zendesk users via search."""
    data = _zd_request("GET", "/search.json", params={"query": f"type:user {query}"})
    users = [
        _user_summary(u)
        for u in data.get("results", [])
        if u.get("result_type") == "user"
    ]
    return UserSearchResponse(users=users, count=len(users), query=query).model_dump()


@mcp.tool()
def find_org(query: str) -> Dict[str, Any]:
    """Find Zendesk organizations via search."""
    data = _zd_request("GET", "/search.json", params={"query": f"type:organization {query}"})
    orgs = [
        OrganizationSummary(
            id=o["id"],
            name=o.get("name"),
            shared_tickets=o.get("shared_tickets"),
            shared_comments=o.get("shared_comments"),
            details=o.get("details"),
            notes=o.get("notes"),
        )
        for o in data.get("results", [])
        if o.get("result_type") == "organization"
    ]
    return OrganizationSearchResponse(organizations=orgs, count=len(orgs), query=query).model_dump()


@mcp.tool()
def list_groups() -> Dict[str, Any]:
    """List Zendesk groups."""
    data = _zd_request("GET", "/groups.json")
    groups = [_group_summary(group) for group in data.get("groups", [])]
    return GroupListResponse(groups=groups, count=len(groups)).model_dump()


@mcp.tool()
def list_ticket_fields() -> Dict[str, Any]:
    """List Zendesk ticket fields and custom field metadata."""
    data = _zd_request("GET", "/ticket_fields.json")
    ticket_fields = [_ticket_field_summary(ticket_field) for ticket_field in data.get("ticket_fields", [])]
    return TicketFieldListResponse(ticket_fields=ticket_fields, count=len(ticket_fields)).model_dump()


@mcp.tool()
def list_views() -> Dict[str, Any]:
    """List Zendesk ticket views."""
    data = _zd_request("GET", "/views.json")
    views = [_view_summary(view) for view in data.get("views", [])]
    return ViewListResponse(views=views, count=len(views)).model_dump()


@mcp.tool()
def get_view_tickets(view_id: int, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
    """List tickets returned by a Zendesk view."""
    per_page = max(1, min(per_page, 100))
    data = _zd_request(
        "GET",
        f"/views/{view_id}/tickets.json",
        params={"page": page, "per_page": per_page},
    )
    tickets = [_ticket_summary(ticket) for ticket in data.get("tickets", [])]
    return TicketListResponse(tickets=tickets, count=len(tickets), query=f"view:{view_id}").model_dump()


@mcp.tool()
def get_ticket_metrics(ticket_id: int) -> Dict[str, Any]:
    """Fetch Zendesk ticket metrics for SLA and handling analysis."""
    data = _zd_request("GET", f"/tickets/{ticket_id}/metrics.json")
    metrics = data["ticket_metric"]
    return TicketMetricsResponse(
        ticket_id=ticket_id,
        reply_time_in_minutes=metrics.get("reply_time_in_minutes"),
        full_resolution_time_in_minutes=metrics.get("full_resolution_time_in_minutes"),
        agent_wait_time_in_minutes=metrics.get("agent_wait_time_in_minutes"),
        requester_wait_time_in_minutes=metrics.get("requester_wait_time_in_minutes"),
        on_hold_time_in_minutes=metrics.get("on_hold_time_in_minutes"),
        group_stations=metrics.get("group_stations"),
        assignee_stations=metrics.get("assignee_stations"),
        reopens=metrics.get("reopens"),
        replies=metrics.get("replies"),
        assignee_updated_at=metrics.get("assignee_updated_at"),
        requester_updated_at=metrics.get("requester_updated_at"),
        status_updated_at=metrics.get("status_updated_at"),
        initially_assigned_at=metrics.get("initially_assigned_at"),
        assigned_at=metrics.get("assigned_at"),
        solved_at=metrics.get("solved_at"),
        latest_comment_added_at=metrics.get("latest_comment_added_at"),
    ).model_dump()


@mcp.tool()
def search_kb(query: str, locale: Optional[str] = None) -> Dict[str, Any]:
    """Search Help Center articles."""
    params: Dict[str, Any] = {"query": query, "page[size]": HELP_CENTER_PAGE_SIZE}
    if locale:
        params["filter[locale]"] = locale
    data = _zd_request("GET", "/help_center/articles/search.json", params=params)
    articles = [_article_summary(a) for a in data.get("results", [])]
    return KBSearchResponse(articles=articles, count=len(articles), query=query).model_dump()


@mcp.tool()
def find_relevant_articles_for_ticket(ticket_id: int) -> Dict[str, Any]:
    """Search the KB using ticket subject and description as query hints."""
    ticket = get_ticket(ticket_id)
    subject = ticket.get("subject") or ""
    description = ticket.get("description") or ""
    query = f"{subject} {description[:300]}".strip()
    if not query:
        return KBSearchResponse(articles=[], count=0, query="").model_dump()
    return search_kb(query=query)


@mcp.tool()
def suggest_next_action(ticket_id: int) -> Dict[str, Any]:
    """Heuristic next-action suggestion for helpdesk workflows."""
    ticket = get_ticket(ticket_id)
    comments = get_ticket_comments(ticket_id)["comments"]

    rationale: List[str] = []
    recommendation = "Review the ticket and determine the next operational step."

    status = ticket.get("status")
    priority = ticket.get("priority")
    description = ticket.get("description") or ""
    has_public_reply = any(comment["public"] for comment in comments)
    has_internal_note = any(not comment["public"] for comment in comments)

    if not description.strip():
        recommendation = "Request more information from the requester."
        rationale.append("The ticket has no meaningful description.")
    elif status in {"new", "open"} and not has_public_reply:
        recommendation = "Send an initial public response acknowledging the issue."
        rationale.append("The ticket is active and there is no public reply yet.")
    elif status == "pending":
        recommendation = "Check whether the customer has responded or whether a follow-up is needed."
        rationale.append("Pending tickets often require customer follow-up review.")
    elif priority in {"high", "urgent"} and not has_internal_note:
        recommendation = "Add an internal triage note and review for escalation."
        rationale.append("The ticket is high priority and lacks internal handling context.")
    else:
        recommendation = "Review recent ticket activity and continue standard handling."
        rationale.append("The ticket already has baseline activity recorded.")

    return NextActionResponse(
        ticket_id=ticket_id,
        recommendation=recommendation,
        rationale=rationale,
    ).model_dump()


@mcp.tool()
def detect_escalation_risk(ticket_id: int) -> Dict[str, Any]:
    """Heuristic escalation risk detector."""
    ticket = get_ticket(ticket_id)
    comments = get_ticket_comments(ticket_id)["comments"]

    signals: List[str] = []
    score = 0

    if ticket.get("priority") == "urgent":
        score += 2
        signals.append("Ticket priority is urgent.")
    elif ticket.get("priority") == "high":
        score += 1
        signals.append("Ticket priority is high.")

    if len(comments) >= 8:
        score += 2
        signals.append("Long comment thread suggests complexity or friction.")
    elif len(comments) >= 4:
        score += 1
        signals.append("Multiple replies suggest ongoing back-and-forth.")

    description = (ticket.get("description") or "").lower()
    escalation_terms = ["urgent", "escalate", "angry", "frustrated", "outage", "sev", "vip"]
    for term in escalation_terms:
        if term in description:
            score += 1
            signals.append(f"Ticket description contains escalation indicator: {term}")
            break

    if score >= 4:
        level: Literal["low", "medium", "high"] = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    return EscalationRiskResponse(ticket_id=ticket_id, risk_level=level, signals=signals).model_dump()


@mcp.resource("zendesk://knowledge-base")
def knowledge_base() -> Dict[str, Any]:
    """Fetch a compact snapshot of Help Center articles."""
    data = _zd_request(
        "GET",
        "/help_center/articles.json",
        params={"page[size]": HELP_CENTER_PAGE_SIZE},
    )
    articles = [_article_summary(a).model_dump() for a in data.get("articles", [])]
    return {"articles": articles, "count": len(articles)}


@mcp.prompt()
def analyze_ticket(ticket_json: str) -> str:
    """Prompt template for ticket analysis."""
    return (
        "Analyze this Zendesk ticket.\n\n"
        f"{ticket_json}\n\n"
        "Include:\n"
        "- summary\n"
        "- likely issue type\n"
        "- urgency and customer impact\n"
        "- missing information\n"
        "- recommended next action"
    )


@mcp.prompt()
def draft_ticket_response(ticket_json: str) -> str:
    """Prompt template for drafting a support response."""
    return (
        "Draft a professional customer-facing support response for this ticket.\n\n"
        f"{ticket_json}\n\n"
        "Tone:\n"
        "- clear\n"
        "- helpful\n"
        "- concise\n"
        "- not overly apologetic\n"
    )


def main() -> None:
    mcp.run()
