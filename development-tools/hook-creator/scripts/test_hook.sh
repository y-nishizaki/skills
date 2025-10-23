#!/bin/bash
#
# Hook Testing Script
#
# Tests Claude Code hooks by simulating hook events with dummy data.
#
# Usage:
#   ./test_hook.sh <command> <event-name> [file-path]
#
# Examples:
#   ./test_hook.sh "jq -r '.tool_input.file_path'" PostToolUse test.ts
#   ./test_hook.sh "jq -r '.hook_event_name'" Notification
#   ./test_hook.sh "echo 'Branch:' && git branch --show-current" UserPromptSubmit
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to generate dummy event data
generate_event_data() {
    local event_name="$1"
    local file_path="${2:-test.ts}"

    case "$event_name" in
        PreToolUse|PostToolUse)
            cat <<EOF
{
  "session_id": "test-session-123",
  "transcript_path": "/tmp/transcript.json",
  "cwd": "$(pwd)",
  "hook_event_name": "$event_name",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "$file_path",
    "old_string": "const x = 1;",
    "new_string": "const x = 2;"
  }
}
EOF
            ;;
        UserPromptSubmit)
            cat <<EOF
{
  "session_id": "test-session-123",
  "transcript_path": "/tmp/transcript.json",
  "cwd": "$(pwd)",
  "hook_event_name": "$event_name",
  "prompt": "Write a TypeScript function"
}
EOF
            ;;
        SessionStart)
            cat <<EOF
{
  "session_id": "test-session-123",
  "transcript_path": "/tmp/transcript.json",
  "cwd": "$(pwd)",
  "hook_event_name": "$event_name",
  "session_start_type": "startup"
}
EOF
            ;;
        PreCompact)
            cat <<EOF
{
  "session_id": "test-session-123",
  "transcript_path": "/tmp/transcript.json",
  "cwd": "$(pwd)",
  "hook_event_name": "$event_name",
  "compact_type": "manual"
}
EOF
            ;;
        *)
            cat <<EOF
{
  "session_id": "test-session-123",
  "transcript_path": "/tmp/transcript.json",
  "cwd": "$(pwd)",
  "hook_event_name": "$event_name"
}
EOF
            ;;
    esac
}

# Function to test a hook command
test_hook() {
    local command="$1"
    local event_name="$2"
    local file_path="${3:-test.ts}"

    print_info "Testing hook command..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Event:   $event_name"
    echo "File:    $file_path"
    echo "Command: $command"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Generate event data
    local event_data
    event_data=$(generate_event_data "$event_name" "$file_path")

    print_info "Input data:"
    echo "$event_data" | jq .
    echo ""

    # Execute the command
    print_info "Executing command..."
    local exit_code=0
    local stdout_output
    local stderr_output

    # Capture stdout and stderr separately
    {
        stdout_output=$(echo "$event_data" | eval "$command" 2>&3)
        exit_code=$?
    } 3>&1 1>&2 | {
        stderr_output=$(cat)
    } 2>&1

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Results:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Display exit code
    if [ $exit_code -eq 0 ]; then
        print_success "Exit code: $exit_code (Success)"
    elif [ $exit_code -eq 2 ]; then
        print_warning "Exit code: $exit_code (Block - would stop Claude)"
    else
        print_error "Exit code: $exit_code (Error - non-blocking)"
    fi

    # Display stdout
    if [ -n "$stdout_output" ]; then
        echo ""
        print_info "Standard Output (stdout):"
        echo "$stdout_output"
    fi

    # Display stderr
    if [ -n "$stderr_output" ]; then
        echo ""
        print_warning "Standard Error (stderr):"
        echo "$stderr_output"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Interpretation
    echo ""
    print_info "Interpretation:"
    case $exit_code in
        0)
            if [ "$event_name" = "UserPromptSubmit" ]; then
                echo "  → Hook succeeded. Output will be added as context to Claude."
            else
                echo "  → Hook succeeded. Output will be shown to the user."
            fi
            ;;
        2)
            echo "  → Hook blocked the operation. Claude will process the stderr message."
            ;;
        *)
            echo "  → Hook failed with non-blocking error. Error will be shown but operation continues."
            ;;
    esac

    return $exit_code
}

# Function to show usage
show_usage() {
    cat <<EOF
Hook Testing Script

Usage:
  $0 <command> <event-name> [file-path]

Arguments:
  command     The hook command to test
  event-name  The hook event to simulate (PreToolUse, PostToolUse, etc.)
  file-path   Optional file path for tool-related events (default: test.ts)

Supported Events:
  PreToolUse          - Before tool execution
  PostToolUse         - After tool execution
  UserPromptSubmit    - When user submits prompt
  Notification        - When Claude notifies
  SessionStart        - When session starts
  SessionEnd          - When session ends
  Stop                - When agent stops
  SubagentStop        - When subagent stops
  PreCompact          - Before context compression

Examples:
  # Test file path extraction
  $0 "jq -r '.tool_input.file_path'" PostToolUse test.ts

  # Test TypeScript file filtering
  $0 "jq -r '.tool_input.file_path | select(test(\"\\\\.tsx?\\\$\"))'" PostToolUse myfile.ts

  # Test file protection
  $0 "jq -r '.tool_input.file_path | select(test(\"production/\"))' | grep -q . && exit 2 || exit 0" PreToolUse production/config.json

  # Test notification
  $0 "echo 'Notification triggered'" Notification

  # Test git context
  $0 "echo 'Branch:' && git branch --show-current" UserPromptSubmit

EOF
}

# Main script
main() {
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi

    local command="$1"
    local event_name="$2"
    local file_path="${3:-test.ts}"

    # Validate event name
    valid_events="PreToolUse PostToolUse UserPromptSubmit Notification SessionStart SessionEnd Stop SubagentStop PreCompact"
    if ! echo "$valid_events" | grep -q "$event_name"; then
        print_error "Invalid event name: $event_name"
        echo ""
        echo "Valid events: $valid_events"
        exit 1
    fi

    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some tests may fail."
        print_info "Install jq with: brew install jq (macOS) or apt-get install jq (Linux)"
        echo ""
    fi

    # Run the test
    test_hook "$command" "$event_name" "$file_path"
}

main "$@"
