# sentinel_poc/run_e2e.ps1
# Orchestrates the Sentinel POC launch, batch processing, grading, and teardown.

$ErrorActionPreference = "Stop"

# 1. Validate Environment Variables
if (-not $env:GEMINI_API_KEY) {
    Write-Host "ERROR: GEMINI_API_KEY environment variable is not set." -ForegroundColor Red
    exit 1
}

# 2. Initialize Docker Environment
Write-Host "Initializing Docker environment (Substrates: Postgres + Neo4j)..." -ForegroundColor Cyan
docker compose up --build --wait

# 3. Execute Batch Pipeline
Write-Host "Executing Sentinel pipeline against dataset batches..." -ForegroundColor Cyan

# Check for local venv
if (Test-Path ".\venv\Scripts\activate.ps1") {
    . .\venv\Scripts\activate.ps1
}

python sentinel/main.py `
  --batch-dir data/sentenil_dirty_datasets `
  --reports output/reports `
  --neo4j-uri bolt://localhost:7687 `
  --neo4j-user neo4j `
  --neo4j-pass sentinel_neo4j

# 4. Execute Grading Harness
Write-Host "Executing external grading harness..." -ForegroundColor Cyan
python tests/grader.py `
  --datasets data/sentenil_dirty_datasets `
  --reports output/reports `
  --out output/

# 5. Teardown Environment
Write-Host "Executing teardown sequence..." -ForegroundColor Yellow
.\teardown.ps1

Write-Host "End-to-end evaluation complete. Review grade_summary.md in the output/ directory." -ForegroundColor Green
