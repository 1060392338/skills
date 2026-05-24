#!/bin/bash
# TuriX-CUA Execution Script for OpenClaw
# This script handles task execution with proper UTF-8 support and config management

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TURIX_DIR="${SCRIPT_DIR}/../../TuriX-CUA"
CONFIG_FILE="${TURIX_DIR}/examples/config.json"
CONDA_ENV="turix_env"

# Default options
USE_PLAN="false"
USE_SKILLS="false"
RESUME="false"
AGENT_ID=""
BACKGROUND="false"
TASK=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
TuriX-CUA Execution Script

Usage:
  $0 "Task description" [OPTIONS]
  $0 --resume <agent_id>

Options:
  --use-plan      Enable planning for complex tasks
  --use-skills    Enable skill selection
  --agent-id      Set custom agent ID for resumption
  --resume        Resume interrupted task (requires agent_id)
  --background    Run in background (non-blocking)
  --help          Show this help message

Examples:
  $0 "Open Chrome and go to github.com"
  $0 "Search AI news and summarize" --use-plan --use-skills
  $0 --resume my-task-001
  $0 "Task" --agent-id custom-123 --background

EOF
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --use-plan)
                USE_PLAN="true"
                shift
                ;;
            --use-skills)
                USE_SKILLS="true"
                shift
                ;;
            --agent-id)
                AGENT_ID="$2"
                shift 2
                ;;
            --resume)
                RESUME="true"
                if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                    AGENT_ID="$2"
                    shift
                fi
                shift
                ;;
            --background)
                BACKGROUND="true"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$TASK" ]]; then
                    TASK="$1"
                fi
                shift
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    # Check if TuriX directory exists
    if [[ ! -d "$TURIX_DIR" ]]; then
        log_error "TuriX-CUA directory not found: $TURIX_DIR"
        log_info "Please clone TuriX-CUA first:"
        echo "  git clone https://github.com/TurixAI/TuriX-CUA.git"
        echo "  cd TuriX-CUA"
        echo "  conda create -n turix_env python=3.12"
        echo "  pip install -r requirements.txt"
        exit 1
    fi

    # Check if conda environment exists
    if ! conda env list | grep -q "$CONDA_ENV"; then
        log_error "Conda environment '$CONDA_ENV' not found"
        log_info "Create it with: conda create -n turix_env python=3.12"
        exit 1
    fi

    # Check if config file exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warning "Config file not found, creating default..."
        mkdir -p "$(dirname "$CONFIG_FILE")"
        cat > "$CONFIG_FILE" << 'CONFIG_EOF'
{
  "agent": {
    "task": "",
    "use_plan": false,
    "use_skills": false,
    "resume": false,
    "max_steps": 100,
    "max_actions_per_step": 5
  },
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "turix-memory-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "turix-planner-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  }
}
CONFIG_EOF
        log_success "Default config created. Please edit API keys in: $CONFIG_FILE"
    fi
}

# Update config using Python (UTF-8 safe)
update_config() {
    log_info "Updating configuration..."
    
    python3 << PYTHON_EOF
import json
import os
import sys
from datetime import datetime

config_path = "$CONFIG_FILE"
task = '''$TASK'''
use_plan = "$USE_PLAN" == "true"
use_skills = "$USE_SKILLS" == "true"
resume = "$RESUME" == "true"
agent_id = "$AGENT_ID" or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Read config with UTF-8
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Config file not found: {config_path}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Invalid JSON in config: {e}", file=sys.stderr)
    sys.exit(1)

# Update agent settings
if 'agent' not in data:
    data['agent'] = {}

if task:
    data['agent']['task'] = task
data['agent']['use_plan'] = use_plan
data['agent']['use_skills'] = use_skills
data['agent']['resume'] = resume
data['agent']['agent_id'] = agent_id

# Write config with UTF-8 (ensure_ascii=False preserves non-ASCII)
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Agent ID: {agent_id}")
print(f"Task: {task[:50]}..." if len(task) > 50 else f"Task: {task}")
print(f"Use Plan: {use_plan}")
print(f"Use Skills: {use_skills}")
print(f"Resume: {resume}")
PYTHON_EOF
}

# Run TuriX
run_turix() {
    log_info "Starting TuriX-CUA..."
    log_info "Working directory: $TURIX_DIR"
    
    # Set PATH to include /usr/sbin (for screencapture)
    export PATH="/usr/sbin:$PATH"
    
    # Activate conda environment and run
    cd "$TURIX_DIR"
    
    if [[ "$BACKGROUND" == "true" ]]; then
        log_info "Running in background..."
        conda run -n "$CONDA_ENV" python examples/main.py > /tmp/turix_$$.log 2>&1 &
        TURIX_PID=$!
        echo $TURIX_PID > /tmp/turix_$$.pid
        log_success "TuriX started in background (PID: $TURIX_PID)"
        log_info "Logs: /tmp/turix_$$.log"
        log_info "Monitor with: tail -f $TURIX_DIR/.turix_tmp/logging.log"
    else
        log_info "Running in foreground (press Ctrl+C to stop)..."
        log_info "Force stop hotkey: Cmd+Shift+2"
        conda run -n "$CONDA_ENV" python examples/main.py
    fi
}

# Check if TuriX is running
check_status() {
    if pgrep -f "python.*examples/main.py" > /dev/null; then
        log_success "TuriX is currently running"
        ps aux | grep "python.*examples/main.py" | grep -v grep
    else
        log_info "TuriX is not running"
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    # If no task and not resuming, show status
    if [[ -z "$TASK" && "$RESUME" == "false" ]]; then
        check_status
        exit 0
    fi
    
    # If resuming without agent_id
    if [[ "$RESUME" == "true" && -z "$AGENT_ID" ]]; then
        log_error "Resume requires agent_id"
        log_info "Usage: $0 --resume <agent_id>"
        exit 1
    fi
    
    check_prerequisites
    update_config
    run_turix
}

# Run main
main "$@"
