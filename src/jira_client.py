# src/jira_client.py
# TAM - Team Activity Monitor
# Handles all JIRA API interactions
# Supports mock mode for testing and demo purposes

import json
import requests
from requests.auth import HTTPBasicAuth
from config.config import (
    JIRA_BASE_URL,
    JIRA_EMAIL,
    JIRA_API_TOKEN,
    USE_MOCK_DATA
)


JIRA_MAX_RESULTS = 10
JIRA_MAX_CHANGELOG = 3


auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

# --- mock data loader ---

def _load_mock_jira_data():
    """Load mock JIRA data from JSON file."""
    try:
        with open("data/jira_issues.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _find_jira_username(name):
    """
    Find JIRA username from members.json by matching display name.
    Supports partial and case-insensitive matching.
    """
    try:
        with open("data/members.json") as f:
            members = json.load(f)
        name_lower = name.lower()
        for member in members:
            if (name_lower in member["name"].lower() or
                name_lower in member["jira_username"].lower()):
                return member["jira_username"]
    except FileNotFoundError:
        pass
    return None


# --- mock implementations ---

def _mock_get_user_issues(username):
    """Return mock JIRA issues for a given username."""
    data = _load_mock_jira_data()

    # try direct match first
    if username in data:
        mock_data = data[username]
    else:
        # try resolving via members.json
        resolved = _find_jira_username(username)
        if resolved and resolved in data:
            mock_data = data[resolved]
        else:
            return {"error": f"User '{username}' not found in mock data"}

    issues = []
    for issue in mock_data["issues"][:JIRA_MAX_RESULTS]:
        fields = issue.get("fields", {})
        issues.append({
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "updated": fields.get("updated", "")[:10]
        })

    return {"issues": issues, "total": mock_data.get("total", len(issues))}


def _mock_get_issue_updates(issue_key):
    """Return mock changelog updates for a specific issue key."""
    data = _load_mock_jira_data()

    for username, user_data in data.items():
        for issue in user_data["issues"]:
            if issue["key"] == issue_key:
                fields = issue.get("fields", {})
                changelog = issue.get("changelog", {}).get("histories", [])[-JIRA_MAX_CHANGELOG:]
                recent_changes = []
                for entry in changelog:
                    for item in entry.get("items", []):
                        recent_changes.append({
                            "field": item.get("field"),
                            "from": item.get("fromString"),
                            "to": item.get("toString"),
                            "date": entry.get("created", "")[:10]
                        })
                return {
                    "key": issue_key,
                    "summary": fields.get("summary"),
                    "status": fields.get("status", {}).get("name"),
                    "priority": fields.get("priority", {}).get("name"),
                    "updated": fields.get("updated", "")[:10],
                    "recent_changes": recent_changes
                }

    return {"error": f"Issue '{issue_key}' not found in mock data"}


# --- real API implementations ---

def _real_get_user_issues(username):
    """Fetch open JIRA issues assigned to a user via real API."""
    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {"error": "JIRA credentials not configured"}

    jql = f'assignee = "{username}" ORDER BY updated DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "maxResults": JIRA_MAX_RESULTS,
        "fields": "summary,status,priority,updated,assignee"
    }

    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)

        if response.status_code == 401:
            return {"error": "JIRA authentication failed — check your credentials"}
        if response.status_code == 400:
            return {"error": f"JIRA query failed — user '{username}' may not exist"}
        if response.status_code != 200:
            return {"error": f"JIRA returned status {response.status_code}"}

        data = response.json()
        issues = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "priority": fields.get("priority", {}).get("name"),
                "updated": fields.get("updated", "")[:10]
            })

        return {"issues": issues, "total": data.get("total", 0)}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to JIRA — check your JIRA_BASE_URL"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def _real_get_issue_updates(issue_key):
    """Fetch status and recent updates for a specific issue via real API."""
    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {"error": "JIRA credentials not configured"}

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    params = {
        "fields": "summary,status,priority,updated,comment",
        "expand": "changelog"
    }

    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)

        if response.status_code == 401:
            return {"error": "JIRA authentication failed — check your credentials"}
        if response.status_code == 404:
            return {"error": f"Issue '{issue_key}' not found"}
        if response.status_code != 200:
            return {"error": f"JIRA returned status {response.status_code}"}

        data = response.json()
        fields = data.get("fields", {})
        changelog = data.get("changelog", {}).get("histories", [])[-JIRA_MAX_CHANGELOG:]
        recent_changes = []
        for entry in changelog:
            for item in entry.get("items", []):
                recent_changes.append({
                    "field": item.get("field"),
                    "from": item.get("fromString"),
                    "to": item.get("toString"),
                    "date": entry.get("created", "")[:10]
                })

        return {
            "key": issue_key,
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "updated": fields.get("updated", "")[:10],
            "recent_changes": recent_changes
        }

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to JIRA — check your JIRA_BASE_URL"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# --- public interface ---

def get_user_issues(username):
    return _mock_get_user_issues(username) if USE_MOCK_DATA else _real_get_user_issues(username)


def get_issue_updates(issue_key):
    return _mock_get_issue_updates(issue_key) if USE_MOCK_DATA else _real_get_issue_updates(issue_key)