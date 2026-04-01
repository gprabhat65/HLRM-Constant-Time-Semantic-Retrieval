Write-Host "Starting HLRM System..."
Write-Host "Launching Backend..."
start "HLRM Backend" cmd /k "uvicorn main:app --reload"

Write-Host "Launching Frontend..."
Set-Location frontend
npm run dev
