# src/jira_client.py
# TAM - Team Activity Monitor
# Handles all JIRA API interactions

import requests
from requests.auth import HTTPBasicAuth
from config.config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

JIRA_MAX_RESULTS = 10
JIRA_MAX_CHANGELOG = 3

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

def get_user_issues(username):
    """
    Fetch open/in-progress JIRA issues assigned to a user.
    username: JIRA account ID or display name
    """
    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {"error": "JIRA credentials not configured"}

    # JQL query - get issues assigned to user
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
                "updated": fields.get("updated", "")[:10]  # just the date
            })

        return {"issues": issues, "total": data.get("total", 0)}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to JIRA — check your JIRA_BASE_URL"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_issue_updates(issue_key):
    """
    Fetch status and recent updates/changelog for a specific JIRA issue.
    """
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

        # get last n changelog entries
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
