#!/bin/bash

if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python manually and try again."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Pip is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "Installing required Python packages..."
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r ./requirements.txt

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Starting the server..."
uvicorn main:app --reload
