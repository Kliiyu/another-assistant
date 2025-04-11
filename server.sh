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

if [ -f ./.env ]; then
    while IFS='=' read -r key value; do
        if [ "$key" == "OLLAMA_HOST" ]; then
            ollamaHost="$value"
        elif [ "$key" == "OLLAMA_LLM_MODEL" ]; then
            ollamaModel="$value"
        fi
    done < ./.env

    if [ -n "$ollamaHost" ] && [ -n "$ollamaModel" ]; then
        echo "Pulling model $ollamaModel from $ollamaHost..."
        curl -X POST "$ollamaHost/api/pull" -H "Content-Type: application/json" -d "{\"model\":\"$ollamaModel\"}"
    else
        echo "OLLAMA_HOST or OLLAMA_LLM_MODEL is not defined in the .env file."
        exit 1
    fi
else
    echo ".env file not found. Please create one with OLLAMA_HOST and OLLAMA_LLM_MODEL defined."
    exit 1
fi

echo "Starting the server..."
uvicorn main:app --reload
