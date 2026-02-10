#!/bin/bash

# Load user's bashrc for standard profile settings
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# --- Zephyr Environment Setup for VS Code Terminal ---

# 1. Define Zephyr Base Directory
export ZEPHYR_BASE="${HOME}/Zephyr-Suite/sdk/source/zephyr"

# 2. Activate Virtual Environment
# Use absolute path for robustness
VENV_PATH="${HOME}/Zephyr-Suite/sdk/venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo "✅ Zephyr Environment Activated."
    echo "   SDK: ${ZEPHYR_BASE}"
    echo "   VENV: ${VENV_PATH}"
else
    echo "⚠️  Error: Could not find virtual environment at:"
    echo "   $VENV_PATH"
fi

# 3. Define Helper Functions

# Function to activate environment (already run on startup, but available for manual use)
function env_zephyr(){
    if [ -f "$VENV_PATH" ]; then
        source "$VENV_PATH"
        export ZEPHYR_BASE="${HOME}/Zephyr-Suite/sdk/source/zephyr"
        echo "Zephyr environment re-activated."
    else
        echo "Error: Virtual environment not found."
    fi
}

# Function to monitor serial output using 'west espressif monitor'
function comtty (){
    echo "Starting ESP32 Serial Monitor..."
    # Try default monitor first, fallback to specific port if needed
    if ! west espressif monitor; then
        echo "Default monitor failed. Trying specific port /dev/ttyUSB0..."
        west espressif monitor -p /dev/ttyUSB0
    fi
}

# Export functions so they are available in subshells if needed
export -f env_zephyr
export -f comtty

# Summary for the user
echo "---------------------------------------------------"
echo "🛠️  Available Commands:"
echo "   env_zephyr : Re-activate Zephyr environment"
echo "   comtty     : Open Serial Monitor (west espressif monitor)"
echo "---------------------------------------------------"
