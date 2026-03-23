# tests/test_jira_client.py
# TAM - Team Activity Monitor
# Unit tests for JIRA client module

import pytest
from unittest.mock import patch, mock_open
import json
from src.jira_client import get_user_issues, get_issue_updates, _format_time


# --- sample mock data ---

MOCK_JIRA_DATA = {
    "john.smith": {
        "total": 2,
        "issues": [
            {
                "id": "12345",
                "key": "TAM-101",
                "fields": {
                    "summary": "Fix authentication bug",
                    "status": {"name": "In Progress"},
                    "priority": {"name": "High"},
                    "updated": "2026-03-20T10:00:00.000+0000",
                    "timeoriginalestimate": 7200,
                    "timespent": 3600,
                    "assignee": {"displayName": "John Smith"},
                    "comment": {"comments": []}
                },
                "changelog": {
                    "histories": [
                        {
                            "id": "1",
                            "created": "2026-03-19T10:00:00.000+0000",
                            "items": [
                                {
                                    "field": "status",
                                    "fromString": "To Do",
                                    "toString": "In Progress"
                                }
                            ]
                        }
                    ]
                }
            },
            {
                "id": "12346",
                "key": "TAM-102",
                "fields": {
                    "summary": "Add unit tests for payment module",
                    "status": {"name": "To Do"},
                    "priority": {"name": "Medium"},
                    "updated": "2026-03-21T10:00:00.000+0000",
                    "timeoriginalestimate": None,
                    "timespent": None,
                    "assignee": {"displayName": "John Smith"},
                    "comment": {"comments": []}
                },
                "changelog": {"histories": []}
            }
        ]
    }
}

MOCK_MEMBERS = [
    {"name": "John Smith", "jira_username": "john.smith", "github_username": "johnsmith"}
]


class TestFormatTime:
    """Tests for _format_time helper function."""

    def test_format_seconds_to_hours(self):
        assert _format_time(7200) == "2h"

    def test_format_one_hour(self):
        assert _format_time(3600) == "1h"

    def test_format_none_returns_none(self):
        assert _format_time(None) is None

    def test_format_zero_returns_none(self):
        assert _format_time(0) is None

    def test_format_large_value(self):
        assert _format_time(28800) == "8h"


class TestGetUserIssues:
    """Tests for get_user_issues function in mock mode."""

    def _mock_open_router(self, filename, *args, **kwargs):
        """Route open() calls to correct mock data based on filename."""
        if "jira_issues.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_JIRA_DATA))()
        elif "members.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_MEMBERS))()
        raise FileNotFoundError(f"Unexpected file: {filename}")

    def test_get_issues_by_jira_username(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("john.smith")
        assert "issues" in result
        assert len(result["issues"]) == 2
        assert result["issues"][0]["key"] == "TAM-101"

    def test_get_issues_by_display_name(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("John")
        assert "issues" in result
        assert len(result["issues"]) == 2

    def test_get_issues_returns_correct_fields(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("john.smith")
        issue = result["issues"][0]
        assert "key" in issue
        assert "summary" in issue
        assert "status" in issue
        assert "priority" in issue
        assert "updated" in issue
        assert "time_estimate" in issue
        assert "time_spent" in issue

    def test_get_issues_time_estimate_formatted(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("john.smith")
        assert result["issues"][0]["time_estimate"] == "2h"
        assert result["issues"][0]["time_spent"] == "1h"

    def test_get_issues_none_time_estimate(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("john.smith")
        assert result["issues"][1]["time_estimate"] is None
        assert result["issues"][1]["time_spent"] is None

    def test_get_issues_user_not_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_user_issues("unknownuser")
        assert "error" in result

    def test_get_issues_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = get_user_issues("john.smith")
        assert "error" in result


class TestGetIssueUpdates:
    """Tests for get_issue_updates function in mock mode."""

    def _mock_open_router(self, filename, *args, **kwargs):
        if "jira_issues.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_JIRA_DATA))()
        raise FileNotFoundError(f"Unexpected file: {filename}")

    def test_get_issue_updates_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_issue_updates("TAM-101")
        assert result["key"] == "TAM-101"
        assert result["status"] == "In Progress"
        assert len(result["recent_changes"]) == 1

    def test_get_issue_updates_changelog_fields(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_issue_updates("TAM-101")
        change = result["recent_changes"][0]
        assert change["field"] == "status"
        assert change["from"] == "To Do"
        assert change["to"] == "In Progress"

    def test_get_issue_updates_no_changelog(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_issue_updates("TAM-102")
        assert result["key"] == "TAM-102"
        assert result["recent_changes"] == []

    def test_get_issue_updates_not_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_issue_updates("TAM-999")
        assert "error" in result