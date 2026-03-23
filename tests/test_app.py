# tests/test_app.py
# TAM - Team Activity Monitor
# Integration tests for main application logic

import pytest
from unittest.mock import patch
from app import handle_query, fetch_all_data


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
        }
    ],
    "total": 1
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

MOCK_JIRA_UPDATES = {
    "key": "TAM-101",
    "summary": "Fix authentication bug",
    "status": "In Progress",
    "priority": "High",
    "updated": "2026-03-20",
    "recent_changes": []
}

EMPTY_JIRA    = {"issues": [], "total": 0}
EMPTY_COMMITS = {"commits": [], "total": 0}
EMPTY_PRS     = {"pull_requests": [], "total": 0}
EMPTY_REPOS   = {"repos": []}
ERROR_JIRA    = {"error": "User not found"}
ERROR_GITHUB  = {"error": "User not found"}


class TestHandleQuery:
    """Integration tests for handle_query function."""

    def _patch_fetch(self, jira=None, commits=None, prs=None, repos=None, updates=None):
        """Helper to patch fetch_all_data with given return values."""
        return patch("app.fetch_all_data", return_value=(
            jira    or MOCK_JIRA_ISSUES,
            updates or MOCK_JIRA_UPDATES,
            commits or MOCK_COMMITS,
            prs     or MOCK_PULL_REQUESTS,
            repos   or MOCK_REPOS
        ))

    # --- valid queries ---
    def test_basic_working_on_query(self):
        with self._patch_fetch():
            result = handle_query("What is John working on?")
        assert "John" in result
        assert result != ""

    def test_show_me_activity_query(self):
        with self._patch_fetch():
            result = handle_query("Show me recent activity for Sarah")
        assert result != ""

    def test_any_updates_query(self):
        with self._patch_fetch():
            result = handle_query("Any updates on Priya?")
        assert result != ""

    def test_how_is_query(self):
        with self._patch_fetch():
            result = handle_query("How is Ravi doing?")
        assert result != ""

    def test_possessive_query(self):
        with self._patch_fetch():
            result = handle_query("Show me Lisa's pull requests")
        assert result != ""

    # --- invalid queries ---
    def test_invalid_query_returns_helpful_message(self):
        result = handle_query("hello how are you")
        assert "doesn't look like a TAM query" in result

    def test_empty_query(self):
        result = handle_query("")
        assert "doesn't look like a TAM query" in result

    def test_query_with_no_name(self):
        result = handle_query("what is the weather today")
        assert "couldn't find a name" in result

    # --- error cases ---
    def test_user_not_found(self):
        with patch("app.fetch_all_data", return_value=(
            ERROR_JIRA, None, ERROR_GITHUB, ERROR_GITHUB, ERROR_GITHUB
        )):
            result = handle_query("What is unknownperson working on?")
        assert "couldn't find any activity" in result
        assert "Available members" in result

    def test_user_found_but_no_activity(self):
        with patch("app.fetch_all_data", return_value=(
            EMPTY_JIRA, None, EMPTY_COMMITS, EMPTY_PRS, EMPTY_REPOS
        )):
            result = handle_query("What is John working on?")
        assert "couldn't find any recent" in result

    # --- response content ---
    def test_response_contains_jira_data(self):
        with self._patch_fetch():
            result = handle_query("What is John working on?")
        assert "TAM-101" in result

    def test_response_contains_github_data(self):
        with self._patch_fetch():
            result = handle_query("What is John working on?")
        assert "fix: resolve null pointer exception" in result


class TestFetchAllData:
    """Tests for fetch_all_data function."""

    def setup_method(self):
        """Clear cache before each test to avoid cross-test contamination."""
        import app
        app._cache.clear()

    def test_returns_tuple_of_five(self):
        with patch("app.get_user_issues", return_value=MOCK_JIRA_ISSUES), \
             patch("app.get_recent_commits", return_value=MOCK_COMMITS), \
             patch("app.get_pull_requests", return_value=MOCK_PULL_REQUESTS), \
             patch("app.get_contributed_repos", return_value=MOCK_REPOS), \
             patch("app.get_issue_updates", return_value=MOCK_JIRA_UPDATES):
            result = fetch_all_data("John")
        assert len(result) == 5

    def test_fetches_issue_updates_for_first_issue(self):
        with patch("app.get_user_issues", return_value=MOCK_JIRA_ISSUES), \
             patch("app.get_recent_commits", return_value=MOCK_COMMITS), \
             patch("app.get_pull_requests", return_value=MOCK_PULL_REQUESTS), \
             patch("app.get_contributed_repos", return_value=MOCK_REPOS), \
             patch("app.get_issue_updates", return_value=MOCK_JIRA_UPDATES) as mock_updates:
            fetch_all_data("John")
        mock_updates.assert_called_once_with("TAM-101")

    def test_skips_issue_updates_when_no_issues(self):
        with patch("app.get_user_issues", return_value=EMPTY_JIRA), \
             patch("app.get_recent_commits", return_value=MOCK_COMMITS), \
             patch("app.get_pull_requests", return_value=MOCK_PULL_REQUESTS), \
             patch("app.get_contributed_repos", return_value=MOCK_REPOS), \
             patch("app.get_issue_updates", return_value=MOCK_JIRA_UPDATES) as mock_updates:
            result = fetch_all_data("John")
        mock_updates.assert_not_called()
        assert result[1] is None

    def test_uses_cache_on_second_call(self):
        with patch("app.get_user_issues", return_value=MOCK_JIRA_ISSUES) as mock_jira, \
             patch("app.get_recent_commits", return_value=MOCK_COMMITS), \
             patch("app.get_pull_requests", return_value=MOCK_PULL_REQUESTS), \
             patch("app.get_contributed_repos", return_value=MOCK_REPOS), \
             patch("app.get_issue_updates", return_value=MOCK_JIRA_UPDATES):
            fetch_all_data("cachetest")
            fetch_all_data("cachetest")
        # should only call API once due to caching
        mock_jira.assert_called_once()