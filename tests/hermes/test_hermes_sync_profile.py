# -*- coding: utf-8 -*-
"""
Tests for the Hermes profile sync script.

These tests validate:
- --dry-run mode (no copy, no secret validation)
- --apply mode (copy template, no secret validation)
- --check-env mode (validate secrets)
- Source validation
- Template application
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from hermes_sync_profile import (
    validate_profile_sources,
    get_required_env_vars,
    validate_required_env,
    apply_plugin_template,
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repo structure."""
    # Create plugin directory
    plugin_dir = tmp_path / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
    plugin_dir.mkdir(parents=True)

    # Create hermes_plugin template
    hermes_plugin_dir = plugin_dir / "hermes_plugin"
    hermes_plugin_dir.mkdir()
    (hermes_plugin_dir / "__init__.py").write_text("# template")

    # Create profile directory
    profile_dir = tmp_path / "pymia" / "hermes" / "profiles" / "pymiafactory"
    profile_dir.mkdir(parents=True)

    # Create profile.yaml
    (profile_dir / "profile.yaml").write_text("profile: pymiafactory\n")

    # Create required_env.yaml
    (profile_dir / "required_env.yaml").write_text(
        "required:\n  - name: TELEGRAM_BOT_TOKEN\n  - name: SUPERMEMORY_API_KEY\n"
    )

    return tmp_path


class TestValidateProfileSources:
    """Tests for validate_profile_sources function."""

    def test_validate_succeeds_with_all_sources(self, temp_repo):
        """Test that validation succeeds when all sources exist."""
        with patch("hermes_sync_profile.REPO_ROOT", temp_repo):
            sources = validate_profile_sources("pymiafactory")

        assert sources["plugin_dir"].exists()
        assert sources["profile_dir"].exists()
        assert sources["profile_yaml"].exists()
        assert sources["required_env_yaml"].exists()

    def test_validate_fails_without_plugin_dir(self, temp_repo):
        """Test that validation fails when plugin directory is missing."""
        # Remove plugin directory
        plugin_dir = temp_repo / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
        import shutil
        shutil.rmtree(plugin_dir)

        with patch("hermes_sync_profile.REPO_ROOT", temp_repo):
            with pytest.raises(FileNotFoundError, match="Plugin directory not found"):
                validate_profile_sources("pymiafactory")

    def test_validate_fails_without_profile_yaml(self, temp_repo):
        """Test that validation fails when profile.yaml is missing."""
        # Remove profile.yaml
        profile_yaml = temp_repo / "pymia" / "hermes" / "profiles" / "pymiafactory" / "profile.yaml"
        profile_yaml.unlink()

        with patch("hermes_sync_profile.REPO_ROOT", temp_repo):
            with pytest.raises(FileNotFoundError, match="profile.yaml not found"):
                validate_profile_sources("pymiafactory")


class TestGetRequiredEnvVars:
    """Tests for get_required_env_vars function."""

    def test_get_required_env_vars(self, temp_repo):
        """Test that required env vars are extracted correctly."""
        required_env_yaml = (
            temp_repo / "pymia" / "hermes" / "profiles" / "pymiafactory" / "required_env.yaml"
        )
        vars = get_required_env_vars(required_env_yaml)

        assert "TELEGRAM_BOT_TOKEN" in vars
        assert "SUPERMEMORY_API_KEY" in vars
        assert len(vars) == 2


class TestValidateRequiredEnv:
    """Tests for validate_required_env function."""

    def test_validate_returns_missing_vars(self, temp_repo):
        """Test that validation returns missing variable names."""
        required_env_yaml = (
            temp_repo / "pymia" / "hermes" / "profiles" / "pymiafactory" / "required_env.yaml"
        )

        # Ensure vars are not set
        with patch.dict(os.environ, {}, clear=True):
            missing = validate_required_env(required_env_yaml)

        assert "TELEGRAM_BOT_TOKEN" in missing
        assert "SUPERMEMORY_API_KEY" in missing

    def test_validate_returns_empty_when_all_set(self, temp_repo):
        """Test that validation returns empty list when all vars are set."""
        required_env_yaml = (
            temp_repo / "pymia" / "hermes" / "profiles" / "pymiafactory" / "required_env.yaml"
        )

        # Set all required vars
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "SUPERMEMORY_API_KEY": "test_key",
            },
        ):
            missing = validate_required_env(required_env_yaml)

        assert missing == []


class TestApplyPluginTemplate:
    """Tests for apply_plugin_template function."""

    def test_apply_copies_template(self, temp_repo, tmp_path):
        """Test that apply copies the template to target."""
        plugin_dir = temp_repo / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
        target_dir = tmp_path / "target_plugin"

        apply_plugin_template(plugin_dir, target_dir, dry_run=False)

        target_init = target_dir / "__init__.py"
        assert target_init.exists()
        assert target_init.read_text() == "# template"

    def test_apply_dry_run_does_not_copy(self, temp_repo, tmp_path):
        """Test that dry-run does not copy the template."""
        plugin_dir = temp_repo / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
        target_dir = tmp_path / "target_plugin"

        apply_plugin_template(plugin_dir, target_dir, dry_run=True)

        target_init = target_dir / "__init__.py"
        assert not target_init.exists()

    def test_apply_fails_without_template(self, temp_repo, tmp_path):
        """Test that apply fails when template is missing."""
        plugin_dir = temp_repo / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"

        # Remove template
        template_path = plugin_dir / "hermes_plugin" / "__init__.py"
        template_path.unlink()

        target_dir = tmp_path / "target_plugin"

        with pytest.raises(FileNotFoundError, match="Plugin template not found"):
            apply_plugin_template(plugin_dir, target_dir, dry_run=False)

    def test_apply_creates_target_dir(self, temp_repo, tmp_path):
        """Test that apply creates target directory if it doesn't exist."""
        plugin_dir = temp_repo / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
        target_dir = tmp_path / "nonexistent" / "target_plugin"

        assert not target_dir.exists()

        apply_plugin_template(plugin_dir, target_dir, dry_run=False)

        assert target_dir.exists()
        assert (target_dir / "__init__.py").exists()
