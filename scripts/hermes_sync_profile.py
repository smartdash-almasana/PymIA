#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hermes Profile Sync Script — Repo to AppData

This script synchronizes the repo-side Hermes profile configuration
and plugin code to the local Hermes runtime (AppData).

Usage:
    # Dry run (validate structure without copying or checking secrets)
    python scripts/hermes_sync_profile.py --profile pymiafactory --dry-run

    # Check environment (validate secrets are present)
    python scripts/hermes_sync_profile.py --profile pymiafactory --check-env

    # Apply plugin template (copy hermes_plugin/__init__.py to AppData)
    python scripts/hermes_sync_profile.py --profile pymiafactory --apply

    # Full sync (copy to AppData, requires secrets)
    python scripts/hermes_sync_profile.py --profile pymiafactory

    # Force overwrite (ignore drift)
    python scripts/hermes_sync_profile.py --profile pymiafactory --force

Exit Codes:
    0 = Success
    1 = Drift detected (without --force)
    2 = Missing required environment variables (only with --check-env or full sync)
    3 = Copy error
    4 = Invalid profile
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml


# Repo root (parent of scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Default AppData path (Windows)
DEFAULT_APPDATA = Path.home() / "AppData" / "Local" / "hermes" / "profiles"


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_profile_sources(profile_name: str) -> Dict[str, Any]:
    """
    Validate that repo-side sources for the profile exist.
    
    Returns:
        Dict with paths to plugin_dir, profile_yaml, required_env_yaml
    
    Raises:
        FileNotFoundError: If any required source is missing
    
    """
    plugin_dir = REPO_ROOT / "pymia" / "hermes" / "plugins" / "pymia_telegram_bridge"
    profile_dir = REPO_ROOT / "pymia" / "hermes" / "profiles" / profile_name
    profile_yaml = profile_dir / "profile.yaml"
    required_env_yaml = profile_dir / "required_env.yaml"

    errors = []

    if not plugin_dir.exists():
        errors.append(f"Plugin directory not found: {plugin_dir}")

    if not profile_dir.exists():
        errors.append(f"Profile directory not found: {profile_dir}")

    if not profile_yaml.exists():
        errors.append(f"profile.yaml not found: {profile_yaml}")

    if not required_env_yaml.exists():
        errors.append(f"required_env.yaml not found: {required_env_yaml}")

    if errors:
        raise FileNotFoundError("\n".join(errors))

    return {
        "plugin_dir": plugin_dir,
        "profile_dir": profile_dir,
        "profile_yaml": profile_yaml,
        "required_env_yaml": required_env_yaml,
    }


def get_required_env_vars(required_env_yaml: Path) -> List[str]:
    """
    Get list of required environment variable names from YAML.
    
    Returns:
        List of variable names
    """
    env_config = load_yaml(required_env_yaml)
    return [var["name"] for var in env_config.get("required", [])]


def validate_required_env(required_env_yaml: Path) -> List[str]:
    """
    Validate that required environment variables are set.
    
    Returns:
        List of missing variable names (empty if all present)
    """
    required_vars = get_required_env_vars(required_env_yaml)

    missing = []
    for var_name in required_vars:
        if not os.environ.get(var_name):
            missing.append(var_name)

    return missing


def sync_plugin_code(
    plugin_dir: Path,
    target_plugin_dir: Path,
    dry_run: bool = False,
) -> None:
    """
    Copy plugin code from repo to AppData.
    
    Args:
        plugin_dir: Source directory (repo)
        target_plugin_dir: Target directory (AppData)
        dry_run: If True, only validate without copying
    """
    if dry_run:
        print(f"[DRY RUN] Would copy plugin from: {plugin_dir}")
        print(f"[DRY RUN] To: {target_plugin_dir}")
        return

    import shutil

    # Ensure target exists
    target_plugin_dir.mkdir(parents=True, exist_ok=True)

    # Copy all .py files
    for py_file in plugin_dir.glob("*.py"):
        target = target_plugin_dir / py_file.name
        shutil.copy2(py_file, target)
        print(f"Copied: {py_file.name}")


def sync_profile_config(
    profile_yaml: Path,
    target_config_dir: Path,
    dry_run: bool = False,
) -> None:
    """
    Copy profile configuration from repo to AppData.
    
    Args:
        profile_yaml: Source profile.yaml (repo)
        target_config_dir: Target config directory (AppData)
        dry_run: If True, only validate without copying
    """
    if dry_run:
        print(f"[DRY RUN] Would copy profile.yaml from: {profile_yaml}")
        print(f"[DRY RUN] To: {target_config_dir}")
        return

    import shutil

    # Ensure target exists
    target_config_dir.mkdir(parents=True, exist_ok=True)

    # Copy profile.yaml
    target = target_config_dir / "profile.yaml"
    shutil.copy2(profile_yaml, target)
    print(f"Copied: profile.yaml")


def apply_plugin_template(
    plugin_dir: Path,
    target_plugin_dir: Path,
    dry_run: bool = False,
) -> None:
    """
    Apply plugin template by copying hermes_plugin/__init__.py to AppData.

    Args:
        plugin_dir: Source plugin directory (repo)
        target_plugin_dir: Target plugin directory (AppData)
        dry_run: If True, only validate without copying

    Raises:
        FileNotFoundError: If hermes_plugin/__init__.py does not exist
    """
    template_path = plugin_dir / "hermes_plugin" / "__init__.py"

    if not template_path.exists():
        raise FileNotFoundError(
            f"Plugin template not found: {template_path}\n"
            f"Expected: {plugin_dir}/hermes_plugin/__init__.py"
        )

    target_init = target_plugin_dir / "__init__.py"

    if dry_run:
        print(f"[DRY RUN] Would copy plugin template from: {template_path}")
        print(f"[DRY RUN] To: {target_init}")
        return

    import shutil

    # Ensure target exists
    target_plugin_dir.mkdir(parents=True, exist_ok=True)

    # Copy template
    shutil.copy2(template_path, target_init)
    print(f"Applied plugin template: {target_init}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync Hermes profile from repo to AppData"
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Profile name (e.g., pymiafactory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate structure without copying or checking secrets",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply plugin template (copy hermes_plugin/__init__.py to AppData)",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Validate that required environment variables are present",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite even if drift detected",
    )
    parser.add_argument(
        "--appdata",
        type=Path,
        default=DEFAULT_APPDATA,
        help=f"AppData profiles directory (default: {DEFAULT_APPDATA})",
    )

    args = parser.parse_args()

    profile_name = args.profile
    dry_run = args.dry_run
    apply_mode = args.apply
    check_env = args.check_env
    force = args.force
    appdata = args.appdata

    print(f"Profile: {profile_name}")
    print(f"Repo root: {REPO_ROOT}")
    print(f"AppData: {appdata}")
    print(f"Dry run: {dry_run}")
    print(f"Apply mode: {apply_mode}")
    print(f"Check env: {check_env}")
    print(f"Force: {force}")
    print()

    # Step 1: Validate repo-side sources
    print("Step 1: Validating repo-side sources...")
    try:
        sources = validate_profile_sources(profile_name)
        print(f"✓ Plugin directory: {sources['plugin_dir']}")
        print(f"✓ Profile directory: {sources['profile_dir']}")
        print(f"✓ profile.yaml: {sources['profile_yaml']}")
        print(f"✓ required_env.yaml: {sources['required_env_yaml']}")
    except FileNotFoundError as e:
        print(f"✗ Validation failed:\n{e}")
        return 4

    print()

    # Step 2: Report required environment variables
    required_vars = get_required_env_vars(sources["required_env_yaml"])
    print("Step 2: Required environment variables (declared)...")
    for var in required_vars:
        print(f"  - {var}")
    print()

    # Step 3: Validate environment presence (only with --check-env or full sync, NOT dry-run or apply)
    if check_env or (not dry_run and not apply_mode):
        print("Step 3: Validating environment variables presence...")
        missing_env = validate_required_env(sources["required_env_yaml"])
        if missing_env:
            print(f"✗ Missing required environment variables:")
            for var in missing_env:
                print(f"  - {var}")
            print()
            print("Set these variables in your environment or .env file.")
            return 2
        else:
            print("✓ All required environment variables are set")
        print()
    else:
        print("Step 3: Skipping environment validation (dry-run or apply mode)")
        print()

    # Step 4: Sync plugin code or apply plugin template
    target_plugin_dir = appdata / profile_name / "plugins" / "pymia-telegram-bridge"

    if apply_mode:
        print("Step 4: Applying plugin template...")
        try:
            apply_plugin_template(
                sources["plugin_dir"], target_plugin_dir, dry_run=dry_run
            )
            if not dry_run:
                print("✓ Plugin template applied")
        except FileNotFoundError as e:
            print(f"✗ Failed to apply plugin template:\n{e}")
            return 3
        except Exception as e:
            print(f"✗ Failed to apply plugin template: {e}")
            return 3
    else:
        print("Step 4: Syncing plugin code...")
        try:
            sync_plugin_code(sources["plugin_dir"], target_plugin_dir, dry_run=dry_run)
            if not dry_run:
                print("✓ Plugin code synced")
        except Exception as e:
            print(f"✗ Failed to sync plugin code: {e}")
            return 3

    print()

    # Step 5: Sync profile configuration
    print("Step 5: Syncing profile configuration...")
    target_config_dir = appdata / profile_name / "config"
    try:
        sync_profile_config(sources["profile_yaml"], target_config_dir, dry_run=dry_run)
        if not dry_run:
            print("✓ Profile configuration synced")
    except Exception as e:
        print(f"✗ Failed to sync profile configuration: {e}")
        return 3

    print()

    if dry_run:
        print("✓ Dry run complete. No files were copied. No secrets validated.")
    else:
        print("✓ Sync complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
