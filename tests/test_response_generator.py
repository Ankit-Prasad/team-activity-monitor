# tests/test_response_generator.py
# TAM - Team Activity Monitor
# Unit tests for response generator module

import pytest
from unittest.mock import patch, MagicMock
from src.response_generator import (
    generate_response,
    _fallback_response,
    _format_jira_data,
    _format_github_data
)


# --- sample data ---

MOCK_JIRA_ISSUES = {
    "issues": [
        {
            "key": "TAM-101",
            "summary": "Fix authentication bug",
            "status": "In Progress",
            "priority": "High",
            "updated": "2026-03-20",
            "time_estimate": "2h",
            "time_spent": "1h"
        },
        {
            "key": "TAM-102",
            "summary": "Add unit tests",
            "status": "To Do",
            "priority": "Medium",
            "updated": "2026-03-21",
            "time_estimate": None,
            "time_spent": None
        }
    ],
    "total": 2
}

MOCK_JIRA_UPDATES = {
    "key": "TAM-101",
    "summary": "Fix authentication bug",
    "status": "In Progress",
    "priority": "High",
    "updated": "2026-03-20",
    "recent_changes": [
        {
            "field": "status",
            "from": "To Do",
            "to": "In Progress",
            "date": "2026-03-19"
        }
    ]
}

MOCK_COMMITS = {
    "commits": [
        {
            "repo": "autonomize-ai/backend-api",
            "message": "fix: resolve null pointer exception",
            "date": "2026-03-20"
        }
    ],
    "total": 1
}

MOCK_PULL_REQUESTS = {
    "pull_requests": [
        {
            "title": "Add pagination to user listing API",
            "repo": "autonomize-ai/backend-api",
            "url": "https://github.com/autonomize-ai/backend-api/pull/101",
            "updated": "2026-03-21"
        }
    ],
    "total": 1
}

MOCK_REPOS = {
    "repos": [
        {
            "name": "autonomize-ai/backend-api",
            "url": "https://github.com/autonomize-ai/backend-api"
        }
    ]
}

EMPTY_JIRA   = {"issues": [], "total": 0}
EMPTY_COMMITS = {"commits": [], "total": 0}
EMPTY_PRS    = {"pull_requests": [], "total": 0}
EMPTY_REPOS  = {"repos": []}
ERROR_JIRA   = {"error": "JIRA credentials not configured"}
ERROR_GITHUB = {"error": "GitHub token not configured"}


class TestFormatJiraData:
    """Tests for _format_jira_data helper."""

    def test_formats_issues_correctly(self):
        result = _format_jira_data(MOCK_JIRA_ISSUES, None)
        assert "TAM-101" in result
        assert "Fix authentication bug" in result
        assert "In Progress" in result
        assert "High" in result

    def test_includes_time_estimate(self):
        result = _format_jira_data(MOCK_JIRA_ISSUES, None)
        assert "2h" in result

    def test_includes_changelog(self):
        result = _format_jira_data(MOCK_JIRA_ISSUES, MOCK_JIRA_UPDATES)
        assert "To Do" in result
        assert "In Progress" in result

    def test_empty_issues(self):
        result = _format_jira_data(EMPTY_JIRA, None)
        assert "No active issues found" in result

    def test_error_response(self):
        result = _format_jira_data(ERROR_JIRA, None)
        assert "JIRA credentials not configured" in result


class TestFormatGithubData:
    """Tests for _format_github_data helper."""

    def test_formats_commits_correctly(self):
        result = _format_github_data(MOCK_COMMITS, MOCK_PULL_REQUESTS, MOCK_REPOS)
        assert "autonomize-ai/backend-api" in result
        assert "fix: resolve null pointer exception" in result

    def test_formats_prs_correctly(self):
        result = _format_github_data(MOCK_COMMITS, MOCK_PULL_REQUESTS, MOCK_REPOS)
        assert "Add pagination to user listing API" in result

    def test_formats_repos_correctly(self):
        result = _format_github_data(MOCK_COMMITS, MOCK_PULL_REQUESTS, MOCK_REPOS)
        assert "autonomize-ai/backend-api" in result

    def test_empty_commits(self):
        result = _format_github_data(EMPTY_COMMITS, MOCK_PULL_REQUESTS, MOCK_REPOS)
        assert "No recent commits found" in result

    def test_empty_prs(self):
        result = _format_github_data(MOCK_COMMITS, EMPTY_PRS, MOCK_REPOS)
        assert "No open PRs found" in result

    def test_error_commits(self):
        result = _format_github_data(ERROR_GITHUB, MOCK_PULL_REQUESTS, MOCK_REPOS)
        assert "GitHub token not configured" in result


class TestFallbackResponse:
    """Tests for _fallback_response template function."""

    def test_contains_username(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "John" in result

    def test_contains_jira_issues(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "TAM-101" in result
        assert "Fix authentication bug" in result

    def test_contains_commits(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "fix: resolve null pointer exception" in result

    def test_contains_pull_requests(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "Add pagination to user listing API" in result

    def test_contains_priority(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "High" in result

    def test_contains_time_estimate(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "2h" in result

    def test_empty_jira(self):
        result = _fallback_response("John", EMPTY_JIRA, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "No active issues found" in result

    def test_empty_commits(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, EMPTY_COMMITS, MOCK_PULL_REQUESTS)
        assert "No recent commits found" in result

    def test_empty_prs(self):
        result = _fallback_response("John", MOCK_JIRA_ISSUES, MOCK_COMMITS, EMPTY_PRS)
        assert "No open pull requests found" in result

    def test_error_jira(self):
        result = _fallback_response("John", ERROR_JIRA, MOCK_COMMITS, MOCK_PULL_REQUESTS)
        assert "No active issues found" in result


class TestGenerateResponse:
    """Tests for generate_response function."""

    def test_falls_back_when_no_openai_key(self):
        with patch("src.response_generator.OPENAI_API_KEY", ""):
            result = generate_response(
                "John",
                MOCK_JIRA_ISSUES,
                MOCK_JIRA_UPDATES,
                MOCK_COMMITS,
                MOCK_PULL_REQUESTS,
                MOCK_REPOS
            )
        assert "John" in result
        assert "TAM-101" in result

    def test_uses_openai_when_key_present(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "John is working on fixing an auth bug."

        with patch("src.response_generator.OPENAI_API_KEY", "fake-key"), \
             patch("src.response_generator.client.chat.completions.create",
                   return_value=mock_response):
            result = generate_response(
                "John",
                MOCK_JIRA_ISSUES,
                MOCK_JIRA_UPDATES,
                MOCK_COMMITS,
                MOCK_PULL_REQUESTS,
                MOCK_REPOS
            )
        assert result == "John is working on fixing an auth bug."

    def test_falls_back_when_openai_fails(self):
        with patch("src.response_generator.OPENAI_API_KEY", "fake-key"), \
             patch("src.response_generator.client.chat.completions.create",
                   side_effect=Exception("API error")):
            result = generate_response(
                "John",
                MOCK_JIRA_ISSUES,
                MOCK_JIRA_UPDATES,
                MOCK_COMMITS,
                MOCK_PULL_REQUESTS,
                MOCK_REPOS
            )
        assert "John" in result
        assert "TAM-101" in result