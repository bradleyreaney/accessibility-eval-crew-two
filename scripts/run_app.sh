#!/usr/bin/env bash
"""
Launch script for the Accessibility Evaluation Streamlit App
Sets up proper Python path and runs the application
"""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set PYTHONPATH to project root
export PYTHONPATH="$PROJECT_ROOT"

# Run the Streamlit app
echo "Starting Accessibility Evaluation System..."
echo "Project root: $PROJECT_ROOT"
echo "Opening browser at: http://localhost:8502"

streamlit run "$PROJECT_ROOT/app/main.py" --server.port 8502
