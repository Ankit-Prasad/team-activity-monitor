# config/config.py
# TAM - Team Activity Monitor
# Loads all API credentials and config from environment variables

from dotenv import load_dotenv
import os

load_dotenv()

# JIRA
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")  # optional, for org-scoped queries

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # default to 3.5t
OPENAI_MAX_TOKENS = 1000
OPENAI_EXTRACTION_MAX_TOKENS = 20
OPENAI_TEMPERATURE = 0.7
OPENAI_EXTRACTION_TEMPERATURE = 0  # deterministic for name extraction

# Query Parser
NAME_EXTRACTION_MODE = os.getenv("NAME_EXTRACTION_MODE", "basic")
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # default 5 minutes

# Mock Data
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"