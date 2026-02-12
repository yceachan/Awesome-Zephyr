#!/usr/bin/zsh

# --- Zephyr Environment Setup for VS Code Terminal ---

# 1. Define Zephyr Base Directory
export ZEPHYR_BASE="${HOME}/Zephyr-Suite/sdk/source/zephyr"

# 2. Activate Virtual Environment
VENV_PATH="${HOME}/Zephyr-Suite/sdk/venv/bin/activate"
VENV_ROOT="${HOME}/Zephyr-Suite/sdk/venv"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH" 
fi

# 3. Define Helper Functions

function env_zephyr(){
    if [ -f "$VENV_PATH" ]; then
        source "$VENV_PATH"
        export ZEPHYR_BASE="${HOME}/Zephyr-Suite/sdk/source/zephyr"
        echo "Zephyr environment re-activated."
    else
        echo "Error: Virtual environment not found."
    fi
}

function comtty (){
    echo "Starting ESP32 Serial Monitor..."
    if ! west espressif monitor; then
        echo "Default monitor failed. Trying specific port /dev/ttyUSB0..."
        west espressif monitor -p /dev/ttyUSB0
    fi
}

# 4. Delayed Welcome Message 
function zephyr_welcome_message() {
    echo "✅ Zephyr Environment Activated."
    echo "   SDK: ${ZEPHYR_BASE}"
    echo "   VENV: ${VENV_PATH}"
    echo "---------------------------------------------------"
    echo "🛠️  Available Commands:"
    echo "   env_zephyr : Re-activate Zephyr environment"
    echo "   comtty     : Open Serial Monitor (west espressif monitor)"
    echo "---------------------------------------------------"
    
 
}

zephyr_welcome_message
