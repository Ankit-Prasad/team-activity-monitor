# tests/test_query_parser.py
# TAM - Team Activity Monitor
# Unit tests for query parser module

import pytest
from src.query_parser import extract_name, is_valid_query


class TestIsValidQuery:
    """Tests for is_valid_query function."""

    def test_basic_working_on_query(self):
        assert is_valid_query("What is John working on?") == True

    def test_show_me_activity_query(self):
        assert is_valid_query("Show me recent activity for Sarah") == True

    def test_commits_query(self):
        assert is_valid_query("What has Mike committed this week?") == True

    def test_pull_requests_query(self):
        assert is_valid_query("Show me Lisa's pull requests") == True

    def test_tickets_query(self):
        assert is_valid_query("What tickets is Alex working on?") == True

    def test_give_me_update_query(self):
        assert is_valid_query("Give me an update on John") == True

    def test_how_is_query(self):
        assert is_valid_query("How is Ravi doing?") == True

    def test_any_updates_query(self):
        assert is_valid_query("Any updates on Priya?") == True

    def test_tell_me_about_query(self):
        assert is_valid_query("Tell me about Arjun's work") == True

    def test_contributing_query(self):
        assert is_valid_query("What is Lisa contributing to?") == True

    def test_invalid_greeting(self):
        assert is_valid_query("hello how are you") == False

    def test_invalid_random_sentence(self):
        assert is_valid_query("the quick brown fox") == False

    def test_empty_string(self):
        assert is_valid_query("") == False


class TestExtractName:
    """Tests for extract_name function."""

    # --- english names ---
    def test_extract_english_name_what_is(self):
        assert extract_name("What is John working on?") == "John"

    def test_extract_english_name_for(self):
        assert extract_name("Show me recent activity for Sarah") == "Sarah"

    def test_extract_english_name_has(self):
        assert extract_name("What has Mike been working on this week?") == "Mike"

    def test_extract_english_full_name(self):
        assert extract_name("What is John Smith working on?") == "John Smith"

    # --- indian names ---
    def test_extract_indian_name_lowercase(self):
        assert extract_name("What is ravi working on?") == "ravi"

    def test_extract_indian_name_for(self):
        assert extract_name("Show me recent activity for priya") == "priya"

    def test_extract_indian_name_has(self):
        assert extract_name("What has rajesh been working on?") == "rajesh"

    # --- possessives ---
    def test_extract_name_with_possessive(self):
        assert extract_name("Show me Lisa's pull requests") == "Lisa"

    def test_extract_indian_name_with_possessive(self):
        assert extract_name("Show me Ravi's commits") == "Ravi"

    # --- typos ---
    def test_extract_name_with_typo(self):
        assert extract_name("waht is john working on?") == "john"

    # --- varied formats ---
    def test_extract_name_give_me_update(self):
        assert extract_name("Give me an update on John") == "John"

    def test_extract_name_how_is(self):
        assert extract_name("How is Ravi doing?") == "Ravi"

    def test_extract_name_any_updates(self):
        assert extract_name("Any updates on Priya?") == "Priya"

    def test_extract_name_tell_me_about(self):
        assert extract_name("Tell me about Arjun's work") == "Arjun"

    # --- edge cases ---
    def test_extract_name_no_name_present(self):
        assert extract_name("What is the weather today?") is None

    def test_extract_name_empty_string(self):
        assert extract_name("") is None