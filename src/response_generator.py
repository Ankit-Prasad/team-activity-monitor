# src/response_generator.py
# TAM - Team Activity Monitor
# Combines JIRA and GitHub data and generates a conversational response using OpenAI

from openai import OpenAI
from config.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE
)

client = OpenAI(api_key=OPENAI_API_KEY)

# --- data formatters ---

def _format_jira_data(jira_issues, jira_updates):
    """Format JIRA data into a readable string for the prompt."""
    lines = []

    if "error" in jira_issues:
        lines.append(f"JIRA Issues: {jira_issues['error']}")
    else:
        issues = jira_issues.get("issues", [])
        if not issues:
            lines.append("JIRA Issues: No active issues found.")
        else:
            lines.append(f"JIRA Issues ({jira_issues.get('total', 0)} total, showing recent):")
            for issue in issues:
                lines.append(
                    f"  - [{issue['key']}] {issue['summary']} "
                    f"| Status: {issue['status']} "
                    f"| Priority: {issue['priority']} "
                    f"| Updated: {issue['updated']}"
                )

    if jira_updates:
        if "error" in jira_updates:
            lines.append(f"JIRA Recent Updates: {jira_updates['error']}")
        else:
            changes = jira_updates.get("recent_changes", [])
            if changes:
                lines.append(f"Recent changes on {jira_updates.get('key')}:")
                for change in changes:
                    lines.append(
                        f"  - {change['field']} changed from "
                        f"'{change['from']}' to '{change['to']}' on {change['date']}"
                    )

    return "\n".join(lines)


def _format_github_data(commits, pull_requests, repos):
    """Format GitHub data into a readable string for the prompt."""
    lines = []

    # commits
    if "error" in commits:
        lines.append(f"GitHub Commits: {commits['error']}")
    else:
        commit_list = commits.get("commits", [])
        if not commit_list:
            lines.append("GitHub Commits: No recent commits found.")
        else:
            lines.append(f"Recent Commits ({commits.get('total', 0)} total, showing recent):")
            for commit in commit_list:
                lines.append(
                    f"  - [{commit['repo']}] {commit['message']} on {commit['date']}"
                )

    # pull requests
    if "error" in pull_requests:
        lines.append(f"GitHub PRs: {pull_requests['error']}")
    else:
        pr_list = pull_requests.get("pull_requests", [])
        if not pr_list:
            lines.append("GitHub Pull Requests: No open PRs found.")
        else:
            lines.append(f"Open Pull Requests ({pull_requests.get('total', 0)} total):")
            for pr in pr_list:
                lines.append(
                    f"  - [{pr['repo']}] {pr['title']} | Updated: {pr['updated']}"
                )

    # repos
    if "error" in repos:
        lines.append(f"GitHub Repos: {repos['error']}")
    else:
        repo_list = repos.get("repos", [])
        if not repo_list:
            lines.append("GitHub Repos: No recent repository contributions found.")
        else:
            lines.append("Recently Contributing to:")
            for repo in repo_list:
                lines.append(f"  - {repo['name']}")

    return "\n".join(lines)


# --- main response generator ---

def generate_response(username, jira_issues, jira_updates, commits, pull_requests, repos):
    """
    Combine JIRA and GitHub data and generate a conversational
    human-readable response using OpenAI.
    """
    if not OPENAI_API_KEY:
        return _fallback_response(username, jira_issues, commits, pull_requests)

    jira_context = _format_jira_data(jira_issues, jira_updates)
    github_context = _format_github_data(commits, pull_requests, repos)

    prompt = f"""
You are TAM, a helpful Team Activity Monitor assistant.
Below is the activity data for team member '{username}' fetched from JIRA and GitHub.
Summarize what this person is currently working on in a concise, conversational tone.
Highlight key tasks, priorities, and recent progress. 
If data is missing or unavailable, mention it briefly but focus on what is available.

--- JIRA Data ---
{jira_context}

--- GitHub Data ---
{github_context}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are TAM, a team activity assistant. "
                        "You summarize developer activity from JIRA and GitHub "
                        "in a clear, concise, and friendly tone."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[TAM Warning] OpenAI response generation failed: {e}")
        return _fallback_response(username, jira_issues, commits, pull_requests)


def _fallback_response(username, jira_issues, commits, pull_requests):
    """
    Template-based fallback response if OpenAI is unavailable.
    """
    lines = [f"Here's what {username} is working on:\n"]

    # jira
    issues = jira_issues.get("issues", []) if "error" not in jira_issues else []
    if issues:
        lines.append("JIRA Issues:")
        for issue in issues:
            lines.append(f"  - [{issue['key']}] {issue['summary']} ({issue['status']})")
    else:
        lines.append("JIRA: No active issues found.")

    # github commits
    commit_list = commits.get("commits", []) if "error" not in commits else []
    if commit_list:
        lines.append("\nRecent Commits:")
        for commit in commit_list:
            lines.append(f"  - [{commit['repo']}] {commit['message']}")
    else:
        lines.append("\nGitHub: No recent commits found.")

    # pull requests
    pr_list = pull_requests.get("pull_requests", []) if "error" not in pull_requests else []
    if pr_list:
        lines.append("\nOpen Pull Requests:")
        for pr in pr_list:
            lines.append(f"  - [{pr['repo']}] {pr['title']}")
    else:
        lines.append("GitHub: No open pull requests found.")

    return "\n".join(lines)