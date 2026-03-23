# tests/test_github_client.py
# TAM - Team Activity Monitor
# Unit tests for GitHub client module

import pytest
from unittest.mock import patch, mock_open
import json
from src.github_client import get_recent_commits, get_pull_requests, get_contributed_repos


# --- sample mock data ---

MOCK_GITHUB_DATA = {
    "johnsmith": {
        "commits": {
            "total_count": 3,
            "items": [
                {
                    "sha": "abc123",
                    "commit": {
                        "message": "fix: resolve null pointer exception\nsome details",
                        "author": {
                            "name": "John Smith",
                            "email": "john.smith@autonomize.ai",
                            "date": "2026-03-20T10:00:00Z"
                        }
                    },
                    "repository": {
                        "full_name": "autonomize-ai/backend-api",
                        "html_url": "https://github.com/autonomize-ai/backend-api"
                    },
                    "html_url": "https://github.com/autonomize-ai/backend-api/commit/abc123"
                },
                {
                    "sha": "def456",
                    "commit": {
                        "message": "feat: add pagination support",
                        "author": {
                            "name": "John Smith",
                            "email": "john.smith@autonomize.ai",
                            "date": "2026-03-21T10:00:00Z"
                        }
                    },
                    "repository": {
                        "full_name": "autonomize-ai/frontend-app",
                        "html_url": "https://github.com/autonomize-ai/frontend-app"
                    },
                    "html_url": "https://github.com/autonomize-ai/frontend-app/commit/def456"
                },
                {
                    "sha": "ghi789",
                    "commit": {
                        "message": "chore: update dependencies",
                        "author": {
                            "name": "John Smith",
                            "email": "john.smith@autonomize.ai",
                            "date": "2026-03-22T10:00:00Z"
                        }
                    },
                    "repository": {
                        "full_name": "autonomize-ai/backend-api",
                        "html_url": "https://github.com/autonomize-ai/backend-api"
                    },
                    "html_url": "https://github.com/autonomize-ai/backend-api/commit/ghi789"
                }
            ]
        },
        "pull_requests": {
            "total_count": 2,
            "items": [
                {
                    "number": 101,
                    "title": "Add pagination to user listing API",
                    "state": "open",
                    "html_url": "https://github.com/autonomize-ai/backend-api/pull/101",
                    "repository_url": "https://api.github.com/repos/autonomize-ai/backend-api",
                    "updated_at": "2026-03-21T10:00:00Z",
                    "user": {"login": "johnsmith"}
                },
                {
                    "number": 102,
                    "title": "Fix authentication token expiry bug",
                    "state": "open",
                    "html_url": "https://github.com/autonomize-ai/frontend-app/pull/102",
                    "repository_url": "https://api.github.com/repos/autonomize-ai/frontend-app",
                    "updated_at": "2026-03-22T10:00:00Z",
                    "user": {"login": "johnsmith"}
                }
            ]
        },
        "repos": [
            "autonomize-ai/backend-api",
            "autonomize-ai/frontend-app"
        ]
    }
}

MOCK_MEMBERS = [
    {"name": "John Smith", "jira_username": "john.smith", "github_username": "johnsmith"}
]


class TestGetRecentCommits:
    """Tests for get_recent_commits function in mock mode."""

    def _mock_open_router(self, filename, *args, **kwargs):
        if "github_activity.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_GITHUB_DATA))()
        elif "members.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_MEMBERS))()
        raise FileNotFoundError(f"Unexpected file: {filename}")

    def test_get_commits_by_github_username(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("johnsmith")
        assert "commits" in result
        assert len(result["commits"]) == 3

    def test_get_commits_by_display_name(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("John")
        assert "commits" in result
        assert len(result["commits"]) == 3

    def test_get_commits_returns_correct_fields(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("johnsmith")
        commit = result["commits"][0]
        assert "repo" in commit
        assert "message" in commit
        assert "date" in commit

    def test_get_commits_first_line_only(self):
        """Commit message should only return first line."""
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("johnsmith")
        assert "\n" not in result["commits"][0]["message"]

    def test_get_commits_date_format(self):
        """Date should be truncated to YYYY-MM-DD."""
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("johnsmith")
        assert len(result["commits"][0]["date"]) == 10

    def test_get_commits_user_not_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_recent_commits("unknownuser")
        assert "error" in result

    def test_get_commits_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = get_recent_commits("johnsmith")
        assert "error" in result


class TestGetPullRequests:
    """Tests for get_pull_requests function in mock mode."""

    def _mock_open_router(self, filename, *args, **kwargs):
        if "github_activity.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_GITHUB_DATA))()
        elif "members.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_MEMBERS))()
        raise FileNotFoundError(f"Unexpected file: {filename}")

    def test_get_prs_by_username(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_pull_requests("johnsmith")
        assert "pull_requests" in result
        assert len(result["pull_requests"]) == 2

    def test_get_prs_returns_correct_fields(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_pull_requests("johnsmith")
        pr = result["pull_requests"][0]
        assert "title" in pr
        assert "repo" in pr
        assert "url" in pr
        assert "updated" in pr

    def test_get_prs_repo_extracted_correctly(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_pull_requests("johnsmith")
        assert result["pull_requests"][0]["repo"] == "autonomize-ai/backend-api"

    def test_get_prs_date_format(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_pull_requests("johnsmith")
        assert len(result["pull_requests"][0]["updated"]) == 10

    def test_get_prs_user_not_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_pull_requests("unknownuser")
        assert "error" in result


class TestGetContributedRepos:
    """Tests for get_contributed_repos function in mock mode."""

    def _mock_open_router(self, filename, *args, **kwargs):
        if "github_activity.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_GITHUB_DATA))()
        elif "members.json" in filename:
            return mock_open(read_data=json.dumps(MOCK_MEMBERS))()
        raise FileNotFoundError(f"Unexpected file: {filename}")

    def test_get_repos_by_username(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_contributed_repos("johnsmith")
        assert "repos" in result
        assert len(result["repos"]) == 2

    def test_get_repos_returns_correct_fields(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_contributed_repos("johnsmith")
        repo = result["repos"][0]
        assert "name" in repo
        assert "url" in repo

    def test_get_repos_correct_url_format(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_contributed_repos("johnsmith")
        assert result["repos"][0]["url"].startswith("https://github.com/")

    def test_get_repos_user_not_found(self):
        with patch("builtins.open", side_effect=self._mock_open_router):
            result = get_contributed_repos("unknownuser")
        assert "error" in result