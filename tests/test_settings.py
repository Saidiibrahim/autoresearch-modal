"""Tests for the autoresearch settings surface."""

from agent_sandbox.config.settings import Settings


def test_settings_defaults_match_autoresearch_contract():
    settings = Settings()

    assert settings.anthropic_secret_name == "anthropic-secret"
    assert settings.autoresearch_repo_url == "https://github.com/karpathy/autoresearch.git"
    assert settings.autoresearch_base_branch == "master"
    assert settings.autoresearch_workspace_root == "/home/claude/workspaces/autoresearch"
    assert settings.autoresearch_cache_root == "/home/claude/.cache/autoresearch"
