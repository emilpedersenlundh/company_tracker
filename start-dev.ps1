# start-dev.ps1 - Start all services for local development on Windows
# Usage: .\start-dev.ps1

$ErrorActionPreference = "Stop"

# Activate virtual environment
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & $venvActivate
    pip install -r requirements.txt
} else {
    & $venvActivate
}

Write-Host "Starting Company Tracker (development mode)" -ForegroundColor Cyan
Write-Host "  API:      http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:8501" -ForegroundColor Green
Write-Host "  Database: SQLite (company_tracker.db)" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Set environment
$env:APP_ENV = "development"

# Start FastAPI and Streamlit as background jobs
$api = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\Activate.ps1"
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

$frontend = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\Activate.ps1"
    streamlit run frontend/Home.py --server.address 127.0.0.1 --server.port 8501
}

try {
    # Stream output from both jobs
    while ($true) {
        Receive-Job -Job $api -ErrorAction SilentlyContinue
        Receive-Job -Job $frontend -ErrorAction SilentlyContinue

        if ($api.State -eq "Failed") {
            Write-Host "API process failed" -ForegroundColor Red
            Receive-Job -Job $api
            break
        }
        if ($frontend.State -eq "Failed") {
            Write-Host "Frontend process failed" -ForegroundColor Red
            Receive-Job -Job $frontend
            break
        }

        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job -Job $api, $frontend -ErrorAction SilentlyContinue
    Remove-Job -Job $api, $frontend -Force -ErrorAction SilentlyContinue
    Write-Host "All services stopped." -ForegroundColor Cyan
}
