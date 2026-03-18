# src/github_client.py
# TAM - Team Activity Monitor
# Handles all GitHub API interactions
# Supports mock mode for testing and demo purposes

import json
import requests
from config.config import GITHUB_TOKEN, GITHUB_ORG, USE_MOCK_DATA

BASE_URL = "https://api.github.com"
GITHUB_MAX_RESULTS = 10
GITHUB_REPO_FETCH_LIMIT = 30

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


# --- mock data loader ---

def _load_mock_github_data():
    """Load mock GitHub activity data from JSON file."""
    try:
        with open("data/github_activity.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _find_github_username(name):
    """
    Find GitHub username from members.json by matching display name.
    Supports partial and case-insensitive matching.
    """
    try:
        with open("data/members.json") as f:
            members = json.load(f)
        name_lower = name.lower()
        for member in members:
            if (name_lower in member["name"].lower() or
                name_lower in member["github_username"].lower()):
                return member["github_username"]
    except FileNotFoundError:
        pass
    return None


# --- mock implementations ---

def _mock_get_recent_commits(username):
    """Return mock recent commits for a given username."""
    data = _load_mock_github_data()

    if username not in data:
        resolved = _find_github_username(username)
        if resolved and resolved in data:
            username = resolved
        else:
            return {"error": f"User '{username}' not found in mock data"}

    items = data[username]["commits"]["items"][:GITHUB_MAX_RESULTS]
    commits = []
    for item in items:
        commits.append({
            "repo": item.get("repository", {}).get("full_name"),
            "message": item.get("commit", {}).get("message", "").split("\n")[0],
            "date": item.get("commit", {}).get("author", {}).get("date", "")[:10]
        })

    return {
        "commits": commits,
        "total": data[username]["commits"]["total_count"]
    }


def _mock_get_pull_requests(username):
    """Return mock open pull requests for a given username."""
    data = _load_mock_github_data()

    if username not in data:
        resolved = _find_github_username(username)
        if resolved and resolved in data:
            username = resolved
        else:
            return {"error": f"User '{username}' not found in mock data"}

    items = data[username]["pull_requests"]["items"][:GITHUB_MAX_RESULTS]
    prs = []
    for item in items:
        prs.append({
            "title": item.get("title"),
            "repo": item.get("repository_url", "").split("/repos/")[-1],
            "url": item.get("html_url"),
            "updated": item.get("updated_at", "")[:10]
        })

    return {
        "pull_requests": prs,
        "total": data[username]["pull_requests"]["total_count"]
    }


def _mock_get_contributed_repos(username):
    """Return mock contributed repositories for a given username."""
    data = _load_mock_github_data()

    if username not in data:
        resolved = _find_github_username(username)
        if resolved and resolved in data:
            username = resolved
        else:
            return {"error": f"User '{username}' not found in mock data"}

    repos = [
        {"name": repo, "url": f"https://github.com/{repo}"}
        for repo in data[username]["repos"]
    ]

    return {"repos": repos}


# --- real API implementations ---

def _real_get_recent_commits(username):
    """Fetch recent commits by a user via real GitHub API."""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}

    url = f"{BASE_URL}/search/commits"
    params = {
        "q": f"author:{username}" + (f" org:{GITHUB_ORG}" if GITHUB_ORG else ""),
        "sort": "author-date",
        "order": "desc",
        "per_page": GITHUB_MAX_RESULTS
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            return {"error": "GitHub authentication failed — check your token"}
        if response.status_code == 422:
            return {"error": f"User '{username}' not found on GitHub"}
        if response.status_code != 200:
            return {"error": f"GitHub returned status {response.status_code}"}

        data = response.json()
        commits = []
        for item in data.get("items", []):
            commits.append({
                "repo": item.get("repository", {}).get("full_name"),
                "message": item.get("commit", {}).get("message", "").split("\n")[0],
                "date": item.get("commit", {}).get("author", {}).get("date", "")[:10]
            })

        return {"commits": commits, "total": data.get("total_count", 0)}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to GitHub"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def _real_get_pull_requests(username):
    """Fetch open pull requests authored by a user via real GitHub API."""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}

    url = f"{BASE_URL}/search/issues"
    params = {
        "q": f"is:pr is:open author:{username}" + (f" org:{GITHUB_ORG}" if GITHUB_ORG else ""),
        "sort": "updated",
        "order": "desc",
        "per_page": GITHUB_MAX_RESULTS
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            return {"error": "GitHub authentication failed — check your token"}
        if response.status_code == 422:
            return {"error": f"User '{username}' not found on GitHub"}
        if response.status_code != 200:
            return {"error": f"GitHub returned status {response.status_code}"}

        data = response.json()
        prs = []
        for item in data.get("items", []):
            prs.append({
                "title": item.get("title"),
                "repo": item.get("repository_url", "").split("/repos/")[-1],
                "url": item.get("html_url"),
                "updated": item.get("updated_at", "")[:10]
            })

        return {"pull_requests": prs, "total": data.get("total_count", 0)}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to GitHub"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def _real_get_contributed_repos(username):
    """Fetch repositories the user has contributed to via real GitHub API."""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}

    url = f"{BASE_URL}/search/commits"
    params = {
        "q": f"author:{username}" + (f" org:{GITHUB_ORG}" if GITHUB_ORG else ""),
        "sort": "author-date",
        "order": "desc",
        "per_page": GITHUB_REPO_FETCH_LIMIT
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 401:
            return {"error": "GitHub authentication failed — check your token"}
        if response.status_code == 422:
            return {"error": f"User '{username}' not found on GitHub"}
        if response.status_code != 200:
            return {"error": f"GitHub returned status {response.status_code}"}

        data = response.json()
        seen = set()
        repos = []
        for item in data.get("items", []):
            repo = item.get("repository", {})
            full_name = repo.get("full_name")
            if full_name and full_name not in seen:
                seen.add(full_name)
                repos.append({
                    "name": full_name,
                    "url": repo.get("html_url")
                })

        return {"repos": repos}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to GitHub"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


# --- public interface ---

def get_recent_commits(username):
    return _mock_get_recent_commits(username) if USE_MOCK_DATA else _real_get_recent_commits(username)


def get_pull_requests(username):
    return _mock_get_pull_requests(username) if USE_MOCK_DATA else _real_get_pull_requests(username)


def get_contributed_repos(username):
    return _mock_get_contributed_repos(username) if USE_MOCK_DATA else _real_get_contributed_repos(username)