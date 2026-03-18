# scripts/generate_mock_data.py
# TAM - Team Activity Monitor
# Generates realistic mock JIRA and GitHub data for testing and demo purposes

import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# --- team members ---
def _load_team_members():
    """Load team members from members_config.json."""
    try:
        with open("data/members_config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[TAM] Error: data/members_config.json not found.")
        exit(1)

TEAM_MEMBERS = _load_team_members()

# --- constants ---
JIRA_STATUSES    = ["To Do", "In Progress", "In Review", "Blocked", "Done"]
JIRA_PRIORITIES  = ["Highest", "High", "Medium", "Low"]
JIRA_ISSUE_TYPES = ["Bug", "Story", "Task", "Improvement", "Epic"]
JIRA_PROJECTS    = ["TAM", "PLATFORM", "INFRA", "MOBILE", "DATA", "QA"]

GITHUB_ORGS = ["autonomize-ai"]
GITHUB_REPOS = [
    "autonomize-ai/backend-api",
    "autonomize-ai/frontend-app",
    "autonomize-ai/mobile-app",
    "autonomize-ai/data-pipeline",
    "autonomize-ai/infra-terraform",
    "autonomize-ai/auth-service",
    "autonomize-ai/notification-service",
    "autonomize-ai/analytics-dashboard"
]

COMMIT_MESSAGES = [
    "fix: resolve null pointer exception in user service",
    "feat: add pagination support to issues endpoint",
    "refactor: clean up authentication middleware",
    "chore: update dependencies to latest versions",
    "fix: correct date formatting in dashboard",
    "feat: implement caching for frequent queries",
    "docs: update API documentation",
    "test: add unit tests for payment module",
    "fix: handle edge case in data processing pipeline",
    "feat: add retry logic for failed API calls",
    "refactor: extract common utilities to shared module",
    "fix: resolve race condition in async handler",
    "feat: implement dark mode support",
    "chore: upgrade CI/CD pipeline configuration",
    "fix: correct timezone handling in scheduler",
    "feat: add export to CSV functionality",
    "perf: optimize database queries for reports",
    "fix: resolve memory leak in background worker",
    "feat: integrate third party logging service",
    "test: improve test coverage for auth module",
]

PR_TITLES = [
    "Add pagination to user listing API",
    "Fix authentication token expiry bug",
    "Refactor database connection pooling",
    "Implement new dashboard analytics",
    "Update CI pipeline for faster builds",
    "Add support for bulk data export",
    "Fix mobile responsiveness issues",
    "Integrate new payment gateway",
    "Improve error handling across services",
    "Add rate limiting to public endpoints",
    "Migrate legacy endpoints to v2",
    "Fix data sync issue between services",
    "Add multi-language support",
    "Optimise image loading performance",
    "Implement role-based access control",
]

JIRA_SUMMARIES = [
    "Implement user authentication flow",
    "Fix dashboard loading performance",
    "Add export functionality to reports",
    "Resolve API rate limiting issues",
    "Update onboarding documentation",
    "Migrate database to new schema",
    "Fix mobile layout on smaller screens",
    "Add unit tests for payment module",
    "Implement notification service",
    "Refactor legacy authentication code",
    "Add support for bulk user import",
    "Fix data inconsistency in analytics",
    "Improve search functionality",
    "Add multi-factor authentication",
    "Resolve intermittent timeout errors",
    "Implement audit logging",
    "Update third party integrations",
    "Fix memory leak in background jobs",
    "Add dark mode to web application",
    "Optimise CI/CD pipeline",
]


# --- helper functions ---

def random_date_within_last_n_days(n=7):
    """Generate a random datetime within the last n days."""
    now = datetime.utcnow()
    delta = timedelta(
        days=random.randint(0, n),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    return (now - delta).strftime("%Y-%m-%dT%H:%M:%S.000+0000")


def random_date_string(n=7):
    """Generate a random date string within the last n days."""
    now = datetime.utcnow()
    delta = timedelta(days=random.randint(0, n))
    return (now - delta).strftime("%Y-%m-%d")


# --- generators ---

def generate_jira_issues():
    """
    Generate mock JIRA issues for all team members.
    Mimics the structure returned by JIRA REST API v3.
    """
    all_issues = {}

    for member in TEAM_MEMBERS:
        username = member["jira_username"]
        issues = []
        num_issues = random.randint(3, 6)

        for i in range(num_issues):
            project = random.choice(JIRA_PROJECTS)
            issue_num = random.randint(100, 999)
            issue_key = f"{project}-{issue_num}"
            status = random.choice(JIRA_STATUSES)
            priority = random.choice(JIRA_PRIORITIES)
            issue_type = random.choice(JIRA_ISSUE_TYPES)
            updated = random_date_within_last_n_days(7)

            # generate changelog entries
            changelog_entries = []
            num_changes = random.randint(1, 3)
            for _ in range(num_changes):
                old_status = random.choice(JIRA_STATUSES)
                new_status = random.choice(JIRA_STATUSES)
                changelog_entries.append({
                    "id": str(fake.random_int(min=10000, max=99999)),
                    "created": random_date_within_last_n_days(7),
                    "items": [
                        {
                            "field": "status",
                            "fromString": old_status,
                            "toString": new_status
                        }
                    ]
                })

            issues.append({
                "id": str(fake.random_int(min=10000, max=99999)),
                "key": issue_key,
                "fields": {
                    "summary": random.choice(JIRA_SUMMARIES),
                    "status": {
                        "name": status,
                        "statusCategory": {
                            "name": "Done" if status == "Done" else "In Progress"
                        }
                    },
                    "priority": {"name": priority},
                    "issuetype": {"name": issue_type},
                    "updated": updated,
                    "assignee": {
                        "displayName": member["name"],
                        "emailAddress": f"{username}@autonomize.ai"
                    },
                    "comment": {
                        "comments": [
                            {
                                "body": fake.sentence(),
                                "created": random_date_within_last_n_days(7)
                            }
                            for _ in range(random.randint(0, 3))
                        ]
                    }
                },
                "changelog": {
                    "histories": changelog_entries
                }
            })

        all_issues[username] = {
            "issues": issues,
            "total": len(issues)
        }

    return all_issues


def generate_github_activity():
    """
    Generate mock GitHub activity for all team members.
    Mimics the structure returned by GitHub REST API search endpoints.
    """
    all_activity = {}

    for member in TEAM_MEMBERS:
        username = member["github_username"]

        # --- commits ---
        commits = []
        num_commits = random.randint(5, 10)
        commit_repos = random.sample(GITHUB_REPOS, min(3, len(GITHUB_REPOS)))

        for _ in range(num_commits):
            repo = random.choice(commit_repos)
            commits.append({
                "sha": fake.sha1(),
                "commit": {
                    "message": random.choice(COMMIT_MESSAGES),
                    "author": {
                        "name": member["name"],
                        "email": f"{username}@autonomize.ai",
                        "date": random_date_within_last_n_days(7)
                    }
                },
                "repository": {
                    "full_name": repo,
                    "html_url": f"https://github.com/{repo}"
                },
                "html_url": f"https://github.com/{repo}/commit/{fake.sha1()}"
            })

        # --- pull requests ---
        pull_requests = []
        num_prs = random.randint(1, 3)
        pr_repos = random.sample(GITHUB_REPOS, min(2, len(GITHUB_REPOS)))

        for i in range(num_prs):
            repo = random.choice(pr_repos)
            pull_requests.append({
                "number": random.randint(100, 999),
                "title": random.choice(PR_TITLES),
                "state": "open",
                "html_url": f"https://github.com/{repo}/pull/{random.randint(100, 999)}",
                "repository_url": f"https://api.github.com/repos/{repo}",
                "updated_at": random_date_within_last_n_days(7),
                "user": {
                    "login": username
                }
            })

        # --- contributed repos ---
        contributed_repos = list(set(
            [c["repository"]["full_name"] for c in commits] +
            [pr["repository_url"].split("/repos/")[-1] for pr in pull_requests]
        ))

        all_activity[username] = {
            "commits": {
                "total_count": len(commits),
                "items": commits
            },
            "pull_requests": {
                "total_count": len(pull_requests),
                "items": pull_requests
            },
            "repos": contributed_repos
        }

    return all_activity


def generate_members():
    """Generate members index file."""
    return TEAM_MEMBERS


# --- main ---

def main():
    # create data dir if it doesn't exist
    os.makedirs("data", exist_ok=True)

    print(f"[TAM] Loading members from data/members_config.json...")
    print(f"[TAM] Generating mock data for {len(TEAM_MEMBERS)} members...")

    # members
    members = generate_members()
    with open("data/members.json", "w") as f:
        json.dump(members, f, indent=2)
    print(f"  ✓ data/members.json — {len(members)} members")

    # jira issues
    jira_issues = generate_jira_issues()
    with open("data/jira_issues.json", "w") as f:
        json.dump(jira_issues, f, indent=2)
    print(f"  ✓ data/jira_issues.json — {sum(v['total'] for v in jira_issues.values())} issues across {len(jira_issues)} members")

    # github activity
    github_activity = generate_github_activity()
    with open("data/github_activity.json", "w") as f:
        json.dump(github_activity, f, indent=2)
    print(f"  ✓ data/github_activity.json — activity for {len(github_activity)} members")

    print("\n[TAM] Mock data generation complete. Files saved to data/")


if __name__ == "__main__":
    main()