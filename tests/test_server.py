import json
import unittest
from unittest.mock import Mock, patch

import requests

from zendesk_mcp_server import server


class ValidationTests(unittest.TestCase):
    def test_clean_text_rejects_blank_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "subject must not be empty"):
            server._clean_text("   ", field_name="subject")

    def test_normalize_tags_rejects_duplicates(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicates"):
            server._normalize_tags(["vip", "vip"])

    def test_update_ticket_requires_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one field"):
            server.update_ticket(ticket_id=123)

    def test_update_ticket_validates_status(self) -> None:
        with self.assertRaisesRegex(ValueError, "status must be one of"):
            server.update_ticket(ticket_id=123, status="started")

    def test_create_ticket_normalizes_inputs_before_writing(self) -> None:
        with patch("zendesk_mcp_server.server._zd_request", return_value={"ticket": {"id": 77}}) as request:
            response = server.create_ticket(
                subject="  Example subject  ",
                description="  Example description  ",
                priority="HIGH",
                ticket_type="Task",
                tags=["alpha", "beta"],
            )

        self.assertEqual(response["ticket_id"], 77)
        request.assert_called_once_with(
            "POST",
            "/tickets.json",
            json={
                "ticket": {
                    "subject": "Example subject",
                    "comment": {"body": "Example description"},
                    "priority": "high",
                    "type": "task",
                    "tags": ["alpha", "beta"],
                }
            },
        )


class ReadOnlyHelperToolTests(unittest.TestCase):
    @patch("zendesk_mcp_server.server._zd_request")
    def test_get_user_maps_detailed_user_fields(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "user": {
                "id": 101,
                "name": "Catherine Vee",
                "email": "cvee@example.com",
                "organization_id": 202,
                "role": "admin",
                "suspended": False,
                "details": "Profile details",
                "notes": "Internal notes",
                "time_zone": "America/Los_Angeles",
                "created_at": "2026-04-13T00:00:00Z",
                "updated_at": "2026-04-13T01:00:00Z",
            }
        }

        response = server.get_user(101)

        self.assertEqual(response["id"], 101)
        self.assertEqual(response["time_zone"], "America/Los_Angeles")
        mock_request.assert_called_once_with("GET", "/users/101.json")

    @patch("zendesk_mcp_server.server._zd_request")
    def test_list_groups_returns_group_summaries(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "groups": [
                {"id": 1, "name": "Support", "description": "Primary queue", "is_default": True, "deleted": False}
            ]
        }

        response = server.list_groups()

        self.assertEqual(response["count"], 1)
        self.assertEqual(response["groups"][0]["name"], "Support")
        mock_request.assert_called_once_with("GET", "/groups.json")

    @patch("zendesk_mcp_server.server._zd_request")
    def test_list_ticket_fields_returns_field_options(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "ticket_fields": [
                {
                    "id": 9,
                    "title": "Priority reason",
                    "type": "tagger",
                    "description": "Why the ticket is urgent",
                    "required": True,
                    "active": True,
                    "visible_in_portal": False,
                    "custom_field_options": [
                        {"name": "Outage", "value": "outage"},
                        {"name": "VIP", "value": "vip"},
                    ],
                }
            ]
        }

        response = server.list_ticket_fields()

        self.assertEqual(response["count"], 1)
        self.assertEqual(response["ticket_fields"][0]["custom_field_options"][0]["value"], "outage")
        mock_request.assert_called_once_with("GET", "/ticket_fields.json")

    @patch("zendesk_mcp_server.server._zd_request")
    def test_list_views_returns_view_summaries(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "views": [
                {"id": 22, "title": "My open tickets", "description": "Assigned open work", "active": True}
            ]
        }

        response = server.list_views()

        self.assertEqual(response["views"][0]["title"], "My open tickets")
        mock_request.assert_called_once_with("GET", "/views.json")

    @patch("zendesk_mcp_server.server._zd_request")
    def test_get_view_tickets_returns_ticket_summaries(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "tickets": [
                {"id": 55, "subject": "Example", "status": "open", "tags": ["vip"], "created_at": "2026-04-13T00:00:00Z"}
            ]
        }

        response = server.get_view_tickets(view_id=44, page=2, per_page=10)

        self.assertEqual(response["count"], 1)
        self.assertEqual(response["query"], "view:44")
        mock_request.assert_called_once_with(
            "GET",
            "/views/44/tickets.json",
            params={"page": 2, "per_page": 10},
        )

    @patch("zendesk_mcp_server.server._zd_request")
    def test_get_ticket_metrics_maps_metrics_payload(self, mock_request: Mock) -> None:
        mock_request.return_value = {
            "ticket_metric": {
                "reply_time_in_minutes": {"business": 5, "calendar": 8},
                "full_resolution_time_in_minutes": {"business": 20, "calendar": 30},
                "reopens": 1,
                "replies": 3,
                "solved_at": "2026-04-13T03:00:00Z",
            }
        }

        response = server.get_ticket_metrics(88)

        self.assertEqual(response["ticket_id"], 88)
        self.assertEqual(response["reopens"], 1)
        self.assertEqual(response["reply_time_in_minutes"]["business"], 5)
        mock_request.assert_called_once_with("GET", "/tickets/88/metrics.json")


class ZendeskRequestTests(unittest.TestCase):
    @patch("zendesk_mcp_server.server._require_config")
    @patch("zendesk_mcp_server.server._auth_mode")
    @patch("zendesk_mcp_server.server._get_access_token")
    @patch("zendesk_mcp_server.server.requests.request")
    def test_zd_request_wraps_http_errors(
        self,
        mock_request: Mock,
        mock_token: Mock,
        mock_auth_mode: Mock,
        _mock_require_config: Mock,
    ) -> None:
        mock_auth_mode.return_value = "oauth"
        mock_token.return_value = "oauth-token"
        response = requests.Response()
        response.status_code = 422
        response._content = json.dumps(
            {"error": "RecordInvalid", "description": "Validation failed"}
        ).encode()
        response.url = "https://example.zendesk.com/api/v2/tickets.json"
        response.request = requests.Request("GET", response.url).prepare()
        mock_response = Mock(wraps=response)
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=response)
        mock_response.json.return_value = {"error": "RecordInvalid", "description": "Validation failed"}
        mock_request.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "Zendesk API request failed \\(422\\): RecordInvalid - Validation failed"):
            server._zd_request("GET", "/tickets.json")

        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer oauth-token")

    @patch("zendesk_mcp_server.server._require_config")
    @patch("zendesk_mcp_server.server._auth_mode")
    @patch("zendesk_mcp_server.server.requests.request")
    def test_zd_request_supports_legacy_api_token_auth(
        self,
        mock_request: Mock,
        mock_auth_mode: Mock,
        _mock_require_config: Mock,
    ) -> None:
        mock_auth_mode.return_value = "api_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"tickets": []}
        mock_request.return_value = mock_response

        with patch("zendesk_mcp_server.server._legacy_auth", return_value=("user/token", "legacy-token")) as mock_legacy_auth:
            response = server._zd_request("GET", "/tickets.json")

        self.assertEqual(response, {"tickets": []})
        mock_legacy_auth.assert_called_once_with()
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["auth"], ("user/token", "legacy-token"))

    @patch("zendesk_mcp_server.server._require_config")
    @patch("zendesk_mcp_server.server._auth_mode")
    @patch("zendesk_mcp_server.server._get_access_token")
    @patch("zendesk_mcp_server.server.requests.request")
    def test_zd_request_wraps_connection_errors(
        self,
        mock_request: Mock,
        mock_token: Mock,
        mock_auth_mode: Mock,
        _mock_require_config: Mock,
    ) -> None:
        mock_auth_mode.return_value = "oauth"
        mock_token.return_value = "oauth-token"
        mock_request.side_effect = requests.ConnectionError("DNS failure")

        with self.assertRaisesRegex(RuntimeError, "Zendesk API request failed: DNS failure"):
            server._zd_request("GET", "/tickets.json")

    @patch("zendesk_mcp_server.server._require_config")
    @patch("zendesk_mcp_server.server._auth_mode")
    @patch("zendesk_mcp_server.server._get_access_token")
    @patch("zendesk_mcp_server.server.requests.request")
    def test_zd_request_refreshes_and_retries_after_401(
        self,
        mock_request: Mock,
        mock_token: Mock,
        mock_auth_mode: Mock,
        _mock_require_config: Mock,
    ) -> None:
        mock_auth_mode.return_value = "oauth"
        mock_token.side_effect = ["expired-token", "fresh-token"]

        first = Mock()
        first.status_code = 401
        first.raise_for_status.return_value = None
        first.json.return_value = {"error": "Unauthorized"}

        second = Mock()
        second.status_code = 200
        second.raise_for_status.return_value = None
        second.json.return_value = {"tickets": []}

        mock_request.side_effect = [first, second]

        response = server._zd_request("GET", "/tickets.json")

        self.assertEqual(response, {"tickets": []})
        self.assertEqual(mock_request.call_count, 2)
        _, first_kwargs = mock_request.call_args_list[0]
        _, second_kwargs = mock_request.call_args_list[1]
        self.assertEqual(first_kwargs["headers"]["Authorization"], "Bearer expired-token")
        self.assertEqual(second_kwargs["headers"]["Authorization"], "Bearer fresh-token")
        self.assertEqual(mock_token.call_args_list[1].kwargs, {"force_refresh": True})


class AuthModeTests(unittest.TestCase):
    def test_auth_mode_prefers_oauth_when_both_are_configured(self) -> None:
        with patch("zendesk_mcp_server.server.CLIENT_ID", "client-id"), patch(
            "zendesk_mcp_server.server.CLIENT_SECRET", "client-secret"
        ), patch("zendesk_mcp_server.server.EMAIL", "agent@example.com"), patch(
            "zendesk_mcp_server.server.API_TOKEN", "legacy-token"
        ):
            self.assertEqual(server._auth_mode(), "oauth")

    def test_require_config_accepts_legacy_api_token_mode(self) -> None:
        with patch("zendesk_mcp_server.server.SUBDOMAIN", "example"), patch(
            "zendesk_mcp_server.server.CLIENT_ID", ""
        ), patch("zendesk_mcp_server.server.CLIENT_SECRET", ""), patch(
            "zendesk_mcp_server.server.EMAIL", "agent@example.com"
        ), patch("zendesk_mcp_server.server.API_TOKEN", "legacy-token"):
            server._require_config()


class OAuthSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_state = server._pending_oauth_state
        server._pending_oauth_state = None

    def tearDown(self) -> None:
        server._pending_oauth_state = self.original_state

    @patch("zendesk_mcp_server.server._require_config")
    def test_begin_oauth_authorization_returns_stateful_url(self, _mock_require_config: Mock) -> None:
        with patch("zendesk_mcp_server.server.CLIENT_ID", "client-id"), patch(
            "zendesk_mcp_server.server.CLIENT_SECRET", "client-secret"
        ):
            response = server.begin_oauth_authorization()

        self.assertIn("authorization_url", response)
        self.assertEqual(response["state"], server._pending_oauth_state)
        self.assertEqual(response["redirect_uri"], server.REDIRECT_URI)

    @patch("zendesk_mcp_server.server._save_token_data")
    @patch("zendesk_mcp_server.server._exchange_authorization_code")
    def test_complete_oauth_authorization_persists_tokens(
        self,
        mock_exchange: Mock,
        mock_save: Mock,
    ) -> None:
        server._pending_oauth_state = "expected-state"
        mock_exchange.return_value = {
            "access_token": "abc",
            "refresh_token": "def",
            "expires_in": 1800,
            "scope": "read write",
            "expires_at": 9999999999,
        }

        response = server.complete_oauth_authorization("auth-code", "expected-state")

        self.assertTrue(response["success"])
        mock_exchange.assert_called_once_with("auth-code")
        mock_save.assert_called_once()
        self.assertIsNone(server._pending_oauth_state)


if __name__ == "__main__":
    unittest.main()
