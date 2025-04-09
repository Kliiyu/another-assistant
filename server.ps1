if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python manually and try again."
    exit 1
}

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "Pip is not installed. Installing pip..."
    python -m ensurepip --upgrade
}

Write-Host "Installing required Python packages..."
python -m venv .\.venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama is not installed. Installing Ollama..."
    $installScriptUrl = "https://ollama.com/install.sh"
    $installScriptPath = "$env:TEMP\install-ollama.sh"
    Invoke-WebRequest -Uri $installScriptUrl -OutFile $installScriptPath
    bash $installScriptPath
}

Write-Host "Starting the server..."
uvicorn main:app --reload
