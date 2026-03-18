# src/github_client.py
# TAM - Team Activity Monitor
# Handles all GitHub API interactions

import requests
from config.config import GITHUB_TOKEN, GITHUB_ORG

GITHUB_MAX_RESULTS = 10
GITHUB_REPO_FETCH_LIMIT = 30

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

def get_recent_commits(username):
    """
    Fetch recent commits by a user across all public repos (or org repos).
    """
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
                "message": item.get("commit", {}).get("message", "").split("\n")[0],  # first line only
                "date": item.get("commit", {}).get("author", {}).get("date", "")[:10]
            })

        return {"commits": commits, "total": data.get("total_count", 0)}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to GitHub"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_pull_requests(username):
    """
    Fetch open pull requests authored by a user.
    """
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


def get_contributed_repos(username):
    """
    Fetch repositories the user has contributed to recently.
    """
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}

    url = f"{BASE_URL}/search/commits"
    params = {
        "q": f"author:{username}" + (f" org:{GITHUB_ORG}" if GITHUB_ORG else ""),
        "sort": "author-date",
        "order": "desc",
        "per_page": GITHUB_REPO_FETCH_LIMIT  # fetch more to extract unique repos
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
