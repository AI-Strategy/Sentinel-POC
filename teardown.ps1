# sentinel_poc/teardown.ps1
# Completely destroys the Sentinel POC containers, networks, and data volumes.

Write-Host "Initiating teardown of the Sentinel POC environment..." -ForegroundColor Cyan

# Stop containers and remove networks, volumes, and orphan containers
docker compose down --volumes --remove-orphans

Write-Host "Teardown complete. All containers, networks, and Neo4j volumes are destroyed." -ForegroundColor Green
