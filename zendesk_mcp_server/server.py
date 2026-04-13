import os
from typing import Any, Dict, List, Literal, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv()

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
    response = requests.request(
        method,
        url,
        params=params,
        json=json,
        auth=_auth(),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


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
        ticket["subject"] = subject
    if status is not None:
        ticket["status"] = status
    if priority is not None:
        ticket["priority"] = priority
    if ticket_type is not None:
        ticket["type"] = ticket_type
    if assignee_id is not None:
        ticket["assignee_id"] = assignee_id
    if requester_id is not None:
        ticket["requester_id"] = requester_id
    if tags is not None:
        ticket["tags"] = tags
    if custom_fields is not None:
        ticket["custom_fields"] = custom_fields
    if due_at is not None:
        ticket["due_at"] = due_at

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
def find_user(query: str) -> Dict[str, Any]:
    """Find Zendesk users via search."""
    data = _zd_request("GET", "/search.json", params={"query": f"type:user {query}"})
    users = [
        UserSummary(
            id=u["id"],
            name=u.get("name"),
            email=u.get("email"),
            organization_id=u.get("organization_id"),
            role=u.get("role"),
            suspended=u.get("suspended"),
        )
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