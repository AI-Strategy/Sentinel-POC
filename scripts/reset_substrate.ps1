# Sentinel Substrate Reset Script (Run as Administrator)
# ---------------------------------------------------------

Write-Host "--- Stopping Native Postgres (Port 5432) ---" -ForegroundColor Cyan
try {
    Stop-Service "postgresql-x64-17" -Force -ErrorAction SilentlyContinue
    Get-Process postgres -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "[SUCCESS] Native Postgres stopped." -ForegroundColor Green
} catch {
    Write-Host "[FAILED] Could not stop native Postgres. Ensure this terminal is ELEVATED (Admin)." -ForegroundColor Red
}

Write-Host "`n--- Cleaning Docker Environment ---" -ForegroundColor Cyan
docker-compose down -v --remove-orphans
docker system prune -f --volumes

Write-Host "`n--- Re-Initializing Substrate (Postgres 18) ---" -ForegroundColor Cyan
docker-compose up -d --force-recreate

Write-Host "`n--- Verifying Connectivity ---" -ForegroundColor Cyan
Start-Sleep -Seconds 5
python scripts\vitals.py

Write-Host "`nSubstrate Reset Complete." -ForegroundColor Green
