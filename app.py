# app.py
# TAM - Team Activity Monitor
# Main application entry point — CLI interface

import concurrent.futures
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


def fetch_all_data(username):
    """
    Fetch JIRA and GitHub data concurrently for a given username.
    Uses ThreadPoolExecutor to run all API calls in parallel.
    """
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

    return jira_issues, jira_updates, commits, pull_requests, repos


def handle_query(query):
    """
    Process a single user query end to end.
    """
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
