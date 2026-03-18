# src/query_parser.py
# TAM - Team Activity Monitor
# Extracts member names from natural language queries
# Supports two modes: "basic" (regex+spacy) or "advanced" (regex+spacy+openai)

import re
import spacy
from config.config import (
    NAME_EXTRACTION_MODE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_EXTRACTION_MAX_TOKENS,
    OPENAI_EXTRACTION_TEMPERATURE
)

# load spacy model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    print("[TAM Warning] spaCy model not found. Run: python3 -m spacy download en_core_web_sm")

STOP_WORDS = {
    "what", "is", "has", "have", "been", "show", "me", "tell",
    "working", "on", "these", "days", "recent", "activity", "for",
    "this", "week", "today", "the", "a", "an", "give", "get",
    "commits", "pull", "requests", "prs", "issues", "tickets"
}

QUERY_KEYWORDS = [
    "what is", "what has", "what was", "show me", "tell me",
    "working on", "activity for", "recent activity", "commits",
    "pull requests", "prs", "issues", "tickets"
]


# --- extraction methods ---

def _extract_via_regex(query):
    """Fast regex-based name extraction for common query patterns."""

    # pattern 1: "for <Name>"
    match = re.search(r'\bfor\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', query)
    if match:
        return _clean_name(match.group(1))

    # pattern 2: "is/has <Name>"
    match = re.search(r'\b(?:is|has)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', query)
    if match:
        return _clean_name(match.group(1))

    # pattern 3: any capitalised word not in stop words
    words = query.split()
    for word in words:
        cleaned = re.sub(r'[^a-zA-Z]', '', word)
        if cleaned and cleaned.lower() not in STOP_WORDS:
            return _clean_name(cleaned)

    return None


def _clean_name(name):
    """
    Post-process extracted name — max 2 words, strip known verb words.
    """
    VERB_WORDS = {"working", "been", "doing", "committed", "worked"}
    words = name.split()
    words = [w for w in words if w.lower() not in VERB_WORDS]
    return " ".join(words[:2]) if words else None


def _extract_via_spacy(query):
    """Use spaCy NER to find PERSON entities in the query."""
    if nlp is None:
        return None

    doc = nlp(query)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return _clean_name(ent.text)

    return None


def _extract_via_openai(query):
    """
    Fallback — ask OpenAI to extract the name.
    Only used in 'advanced' mode when regex and spaCy both fail.
    """
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract person names or usernames from queries. "
                        "Return only the name, nothing else. "
                        "If no name is found, return 'None'."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract the person's name from this query: '{query}'"
                }
            ],
            max_tokens=OPENAI_EXTRACTION_MAX_TOKENS,
            temperature=OPENAI_EXTRACTION_TEMPERATURE
        )

        result = response.choices[0].message.content.strip()
        return None if result.lower() == "none" else result

    except Exception as e:
        print(f"[TAM Warning] OpenAI name extraction failed: {e}")
        return None


# --- main extractor ---

def extract_name(query):
    """
    Extract a person's name from a natural language query.

    basic mode:    regex -> spaCy
    advanced mode: regex -> spaCy -> OpenAI

    Returns the name string or None if not found.
    """
    # always try regex first — fast and works for common patterns
    name = _extract_via_regex(query)
    if name:
        return name

    # spaCy fallback
    name = _extract_via_spacy(query)
    if name:
        return name

    # OpenAI fallback — only in advanced mode
    if NAME_EXTRACTION_MODE == "advanced":
        name = _extract_via_openai(query)
        if name:
            return name

    return None


def is_valid_query(query):
    """Basic check — does this look like a TAM query at all?"""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in QUERY_KEYWORDS)
