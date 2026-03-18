# TAM — Team Activity Monitor

TAM is a CLI-based chatbot that answers natural language questions about team member activity by fetching real-time data from JIRA and GitHub, and generating conversational summaries using OpenAI.

> "What is John working on?" — TAM fetches JIRA tickets and GitHub commits/PRs for John and gives you a clean, readable summary.

---

## Features

- Natural language query parsing with regex + spaCy (supports English and Indian names)
- JIRA integration — fetches assigned issues, statuses, and recent changelog updates
- GitHub integration — fetches recent commits, open pull requests, and contributed repositories
- OpenAI-powered conversational responses with a template-based fallback if OpenAI is unavailable
- Concurrent API calls for faster responses
- Two name extraction modes — `basic` (regex + spaCy) and `advanced` (regex + spaCy + OpenAI)

---

## Project Structure
```
tam/
├── src/
│   ├── jira_client.py        # JIRA API integration
│   ├── github_client.py      # GitHub API integration
│   ├── query_parser.py       # Name extraction from natural language
│   └── response_generator.py # OpenAI response generation
├── config/
│   └── config.py             # Loads all configuration from .env
├── public/                   # Reserved for future web interface
├── app.py                    # Main CLI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Your secrets (never committed)
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- pip3
- Git

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd tam
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 4. Download the spaCy language model
```bash
python3 -m spacy download en_core_web_sm
```

### 5. Configure your environment
Copy the example below into a `.env` file in the project root and fill in your credentials:
```
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token_here

GITHUB_TOKEN=your_github_token_here
GITHUB_ORG=your_github_org_here

OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-3.5-turbo

NAME_EXTRACTION_MODE=basic
```

---

## Configuration

| Variable | Description | Required |
|---|---|---|
| `JIRA_BASE_URL` | Your JIRA instance URL e.g. `https://org.atlassian.net` | Yes |
| `JIRA_EMAIL` | Email associated with your JIRA account | Yes |
| `JIRA_API_TOKEN` | JIRA API token from Atlassian account settings | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `GITHUB_ORG` | GitHub organisation name for scoped queries | No |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | OpenAI model to use, defaults to `gpt-3.5-turbo` | No |
| `NAME_EXTRACTION_MODE` | `basic` (regex + spaCy) or `advanced` (regex + spaCy + OpenAI) | No |

---

## How to Run

### CLI
```bash
python3 app.py
```

You will see the TAM welcome banner and a `You:` prompt. Type your query and TAM will fetch and summarise the activity for that team member.

Type `help` for example queries, `exit` to quit.

### Web Interface
A web interface is planned for a future release. The `public/` directory is reserved for this purpose.

---

## Example Queries
```
What is John working on?
Show me recent activity for Sarah
What has Mike been working on this week?
Show me Lisa's pull requests
What tickets is Alex working on?
What is ravi working on?
Show me recent activity for priya
```

---

## API Credentials

### JIRA API Token
1. Log in to your Atlassian account
2. Go to Account Settings → Security → API Tokens
3. Click Create API Token and copy the value into `.env`

### GitHub Personal Access Token
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate a new token with `repo` and `read:user` scopes
3. Copy the value into `.env`

### OpenAI API Key
1. Go to platform.openai.com
2. Navigate to API Keys and create a new key
3. Copy the value into `.env`