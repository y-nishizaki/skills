#!/usr/bin/env python3
"""
Hook Configuration Validator

Validates Claude Code hook configurations in settings.json files.

Usage:
    python validate_hook.py <path-to-settings.json>

Examples:
    python validate_hook.py ~/.claude/settings.json
    python validate_hook.py .claude/settings.json
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Valid hook event names
VALID_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "UserPromptSubmit",
    "Notification",
    "SessionStart",
    "SessionEnd",
    "Stop",
    "SubagentStop",
    "PreCompact"
}

# Events that support matcher patterns
MATCHER_SUPPORTED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "SessionStart",
    "PreCompact"
}


def validate_json_syntax(file_path: Path) -> Tuple[bool, str, Dict]:
    """
    Validate JSON syntax of the settings file.

    Returns:
        (is_valid, message, data)
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return True, "JSON syntax is valid", data
    except FileNotFoundError:
        return False, f"File not found: {file_path}", {}
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error at line {e.lineno}, column {e.colno}: {e.msg}", {}
    except Exception as e:
        return False, f"Error reading file: {e}", {}


def validate_hook_structure(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate the structure of hook configuration.

    Returns:
        (is_valid, warnings)
    """
    warnings = []

    if "hooks" not in data:
        return False, ["No 'hooks' field found in settings.json"]

    if not isinstance(data["hooks"], list):
        return False, ["'hooks' field must be an array"]

    if len(data["hooks"]) == 0:
        warnings.append("'hooks' array is empty - no hooks configured")

    return True, warnings


def validate_hook_entry(hook_entry: Dict, index: int) -> Tuple[bool, List[str]]:
    """
    Validate a single hook entry.

    Returns:
        (is_valid, errors)
    """
    errors = []

    # Check required fields
    if "matcher" not in hook_entry:
        errors.append(f"Hook entry {index}: Missing required field 'matcher'")
    elif not isinstance(hook_entry["matcher"], str):
        errors.append(f"Hook entry {index}: 'matcher' must be a string")

    if "hooks" not in hook_entry:
        errors.append(f"Hook entry {index}: Missing required field 'hooks'")
        return False, errors

    if not isinstance(hook_entry["hooks"], list):
        errors.append(f"Hook entry {index}: 'hooks' must be an array")
        return False, errors

    # Validate individual hooks
    for hook_idx, hook in enumerate(hook_entry["hooks"]):
        hook_errors = validate_individual_hook(hook, index, hook_idx)
        errors.extend(hook_errors)

    return len(errors) == 0, errors


def validate_individual_hook(hook: Dict, entry_idx: int, hook_idx: int) -> List[str]:
    """
    Validate an individual hook configuration.

    Returns:
        List of error messages
    """
    errors = []
    prefix = f"Hook entry {entry_idx}, hook {hook_idx}"

    # Check required fields
    if "hookEventName" not in hook:
        errors.append(f"{prefix}: Missing required field 'hookEventName'")
    elif hook["hookEventName"] not in VALID_EVENTS:
        errors.append(
            f"{prefix}: Invalid hookEventName '{hook['hookEventName']}'. "
            f"Valid values: {', '.join(sorted(VALID_EVENTS))}"
        )

    if "command" not in hook:
        errors.append(f"{prefix}: Missing required field 'command'")
    elif not isinstance(hook["command"], str):
        errors.append(f"{prefix}: 'command' must be a string")
    elif len(hook["command"].strip()) == 0:
        errors.append(f"{prefix}: 'command' cannot be empty")

    # Check optional fields
    if "timeout" in hook:
        if not isinstance(hook["timeout"], (int, float)):
            errors.append(f"{prefix}: 'timeout' must be a number")
        elif hook["timeout"] <= 0:
            errors.append(f"{prefix}: 'timeout' must be positive")

    return errors


def check_best_practices(data: Dict) -> List[str]:
    """
    Check for best practice violations and potential issues.

    Returns:
        List of warning messages
    """
    warnings = []

    for entry_idx, hook_entry in enumerate(data.get("hooks", [])):
        matcher = hook_entry.get("matcher", "")

        for hook_idx, hook in enumerate(hook_entry.get("hooks", [])):
            event_name = hook.get("hookEventName", "")
            command = hook.get("command", "")
            timeout = hook.get("timeout", 60)

            prefix = f"Hook entry {entry_idx}, hook {hook_idx}"

            # Warn about non-matcher-supported events with specific matchers
            if event_name not in MATCHER_SUPPORTED_EVENTS and matcher != "*":
                warnings.append(
                    f"{prefix}: Event '{event_name}' does not support matcher patterns. "
                    f"Matcher '{matcher}' will be ignored."
                )

            # Warn about long timeouts
            if timeout > 120:
                warnings.append(
                    f"{prefix}: Long timeout ({timeout}s) may cause delays. "
                    "Consider reducing or running command in background."
                )

            # Warn about potential security issues
            if "eval" in command or "exec" in command:
                warnings.append(
                    f"{prefix}: Command contains 'eval' or 'exec' which may be unsafe. "
                    "Ensure input is properly sanitized."
                )

            # Warn about missing error handling
            if "||" not in command and "&&" not in command:
                warnings.append(
                    f"{prefix}: Command lacks error handling (||, &&). "
                    "Consider adding error handling for robustness."
                )

            # Warn about hardcoded paths
            if "/Users/" in command or "C:\\" in command:
                warnings.append(
                    f"{prefix}: Command contains hardcoded paths. "
                    "Consider using environment variables for portability."
                )

    return warnings


def print_summary(is_valid: bool, errors: List[str], warnings: List[str]):
    """Print validation summary."""
    print("\n" + "="*60)
    if is_valid and len(errors) == 0:
        print("✅ Validation PASSED")
    else:
        print("❌ Validation FAILED")
    print("="*60)

    if errors:
        print(f"\n🚫 {len(errors)} Error(s):")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for warning in warnings:
            print(f"  - {warning}")

    if is_valid and len(errors) == 0:
        if len(warnings) == 0:
            print("\n🎉 Your hook configuration is perfect!")
        else:
            print("\n✅ Your hook configuration is valid but has some warnings.")
            print("   Consider addressing them for best practices.")
    else:
        print("\n❌ Please fix the errors above before using this configuration.")


def validate_hooks(file_path: str) -> bool:
    """
    Main validation function.

    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path).expanduser().resolve()

    print(f"🔍 Validating hook configuration: {path}")

    # Step 1: Validate JSON syntax
    is_valid, message, data = validate_json_syntax(path)
    if not is_valid:
        print(f"❌ {message}")
        return False
    print(f"✅ {message}")

    # Step 2: Validate structure
    is_valid, warnings = validate_hook_structure(data)
    if not is_valid:
        print_summary(False, warnings, [])
        return False

    # Step 3: Validate each hook entry
    all_errors = []
    for idx, hook_entry in enumerate(data.get("hooks", [])):
        is_valid, errors = validate_hook_entry(hook_entry, idx)
        all_errors.extend(errors)

    # Step 4: Check best practices
    all_warnings = warnings + check_best_practices(data)

    # Step 5: Print summary
    is_valid = len(all_errors) == 0
    print_summary(is_valid, all_errors, all_warnings)

    return is_valid


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_hook.py <path-to-settings.json>")
        print("\nExamples:")
        print("  python validate_hook.py ~/.claude/settings.json")
        print("  python validate_hook.py .claude/settings.json")
        sys.exit(1)

    file_path = sys.argv[1]
    is_valid = validate_hooks(file_path)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
