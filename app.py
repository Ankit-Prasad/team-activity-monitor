# app.py
# TAM - Team Activity Monitor
# Main application entry point — CLI interface

import time
import concurrent.futures
from config.config import CACHE_TTL
from src.jira_client import get_user_issues, get_issue_updates
from src.github_client import get_recent_commits, get_pull_requests, get_contributed_repos
from src.query_parser import extract_name, is_valid_query
from src.response_generator import generate_response

WELCOME_BANNER = """
╔══════════════════════════════════════════╗
║     TAM — Team Activity Monitor          ║
║     Type 'help' for example queries      ║
║     Type 'exit' to quit                  ║
╚══════════════════════════════════════════╝
"""

HELP_TEXT = """
Example queries:
  - What is John working on?
  - Show me recent activity for Sarah
  - What has Mike been working on this week?
  - Show me Lisa's pull requests
  - What tickets is Alex working on?
"""


# simple in-memory cache — stores results for CACHE_TTL seconds
_cache = {}


def fetch_all_data(username):
    """
    Fetch JIRA and GitHub data concurrently for a given username.
    Uses ThreadPoolExecutor to run all API calls in parallel.
    Results are cached for CACHE_TTL seconds to avoid redundant API calls.
    """
    username_lower = username.lower()
    now = time.time()

    # return cached result if still valid
    if username_lower in _cache:
        cached_at, cached_data = _cache[username_lower]
        if now - cached_at < CACHE_TTL:
            print(f"[TAM] Returning cached data for '{username}'")
            return cached_data
    
    # fetch fresh data concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_jira_issues     = executor.submit(get_user_issues, username)
        future_commits         = executor.submit(get_recent_commits, username)
        future_pull_requests   = executor.submit(get_pull_requests, username)
        future_repos           = executor.submit(get_contributed_repos, username)

        jira_issues   = future_jira_issues.result()
        commits       = future_commits.result()
        pull_requests = future_pull_requests.result()
        repos         = future_repos.result()

    # fetch issue updates for the first jira issue if available
    jira_updates = None
    if "issues" in jira_issues and jira_issues["issues"]:
        first_issue_key = jira_issues["issues"][0]["key"]
        jira_updates = get_issue_updates(first_issue_key)

    result = (jira_issues, jira_updates, commits, pull_requests, repos)

    # store in cache
    _cache[username_lower] = (now, result)

    return result


def handle_query(query):
    if not is_valid_query(query):
        return (
            "That doesn't look like a TAM query. "
            "Try asking something like 'What is John working on?' "
            "or type 'help' for examples."
        )

    username = extract_name(query)
    if not username:
        return (
            "I couldn't find a name in your query. "
            "Try being specific, e.g. 'What is John working on?'"
        )

    print(f"\n[TAM] Fetching activity for '{username}'...")

    jira_issues, jira_updates, commits, pull_requests, repos = fetch_all_data(username)

    # check for user not found vs no activity
    jira_error = "error" in jira_issues
    github_error = "error" in commits

    jira_empty = not jira_issues.get("issues")
    github_empty = not commits.get("commits")

    # user not found
    if jira_error and github_error:
        try:
            import json
            with open("data/members_config.json") as f:
                members = json.load(f)
            names = ", ".join(m["name"].split()[0] for m in members)
        except FileNotFoundError:
            names = "unknown — members_config.json not found"

        return (
            f"I couldn't find any activity for '{username}'. "
            f"Make sure the name matches a team member. "
            f"Available members: {names}."
        )

    # user found but no activity in either system
    if jira_empty and github_empty:
        return (
            f"I found '{username}' in the system but couldn't find "
            f"any recent JIRA issues or GitHub activity. "
            f"They may not have any active work at the moment."
        )

    print("[TAM] Generating response...\n")

    return generate_response(
        username,
        jira_issues,
        jira_updates,
        commits,
        pull_requests,
        repos
    )


def main():
    """
    Main CLI loop.
    """
    print(WELCOME_BANNER)

    while True:
        try:
            query = input("You: ").strip()

            if not query:
                continue

            if query.lower() == "exit":
                print("\n[TAM] Goodbye!")
                break

            if query.lower() == "help":
                print(HELP_TEXT)
                continue

            response = handle_query(query)
            print(f"\nTAM: {response}\n")

        except KeyboardInterrupt:
            print("\n\n[TAM] Goodbye!")
            break


if __name__ == "__main__":
    main()
