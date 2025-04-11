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

if (Test-Path .\.env) {
    $envVars = Get-Content .\.env | ForEach-Object {
        if ($_ -match "^(.*?)=(.*)$") {
            [PSCustomObject]@{ Key = $matches[1]; Value = $matches[2] }
        }
    }

    $ollamaHost = $envVars | Where-Object { $_.Key -eq "OLLAMA_HOST" } | Select-Object -ExpandProperty Value
    $ollamaModel = $envVars | Where-Object { $_.Key -eq "OLLAMA_LLM_MODEL" } | Select-Object -ExpandProperty Value

    if ($ollamaHost -and $ollamaModel) {
        Write-Host "Pulling model $ollamaModel on $ollamaHost..."
        Invoke-RestMethod -Uri "$ollamaHost/api/pull" -Method Post -Body (@{ model = $ollamaModel } | ConvertTo-Json -Depth 10) -ContentType "application/json"
    } else {
        Write-Host "OLLAMA_HOST or OLLAMA_LLM_MODEL is not defined in the .env file."
        exit 1
    }
} else {
    Write-Host ".env file not found. Please create one with OLLAMA_HOST and OLLAMA_LLM_MODEL defined."
    exit 1
}

Write-Host "Starting the server..."
uvicorn main:app --reload
