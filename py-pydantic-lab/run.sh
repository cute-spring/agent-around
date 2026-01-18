#!/bin/bash

# =================================================================
# Python Virtual Env Runner
# =================================================================
# This script ensures that the local virtual environment is set up
# and then executes the target Python script using that environment.
#
# Usage: ./run.sh examples/01-basics/1-basic-generation.py
# =================================================================

set -e

# Configuration
VENV_NAME="venv"
REQUIREMENTS="requirements.txt"

# Get the directory where this run.sh script resides
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="$BASE_DIR/$VENV_NAME"
PYTHON_EXE="$VENV_PATH/bin/python"
PIP_EXE="$VENV_PATH/bin/pip"

# 1. Initialize venv if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "🚀 Initializing virtual environment in $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

# 2. Check if we need to install/update dependencies
# We use a hidden file to track the last sync time with requirements.txt
LAST_SYNC="$VENV_PATH/.last_sync"
REQ_FILE="$BASE_DIR/$REQUIREMENTS"

if [ ! -f "$LAST_SYNC" ] || [ "$REQ_FILE" -nt "$LAST_SYNC" ]; then
    echo "📦 Installing/Updating dependencies from $REQUIREMENTS..."
    "$PIP_EXE" install --upgrade pip
    "$PIP_EXE" install -r "$REQ_FILE"
    touch "$LAST_SYNC"
    echo "✅ Dependencies are up to date."
fi

# 3. Handle arguments
if [ -z "$1" ]; then
    echo "❌ Error: No script provided."
    echo "Usage: $0 <path_to_python_script> [args...]"
    echo "Example: $0 examples/01-basics/1-basic-generation.py"
    exit 1
fi

TARGET_SCRIPT=$1
shift # Shift arguments so $@ contains only script arguments

# Resolve target script path (support both absolute and relative to current or BASE_DIR)
if [ ! -f "$TARGET_SCRIPT" ]; then
    if [ -f "$BASE_DIR/$TARGET_SCRIPT" ]; then
        TARGET_SCRIPT="$BASE_DIR/$TARGET_SCRIPT"
    else
        echo "❌ Error: Script not found: $TARGET_SCRIPT"
        exit 1
    fi
fi

# 4. Run the script
echo "🏃 Executing: $TARGET_SCRIPT"
echo "---------------------------------------------------------"
# Export BASE_DIR to PYTHONPATH so local imports work correctly if needed
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Load .env if it exists in BASE_DIR
if [ -f "$BASE_DIR/.env" ]; then
    export $(grep -v '^#' "$BASE_DIR/.env" | xargs)
fi

"$PYTHON_EXE" "$TARGET_SCRIPT" "$@"
