#!/usr/bin/env bash
# sentinel_poc/teardown.sh
# Completely destroys the Sentinel POC containers, networks, and data volumes.

set -e

echo "Initiating teardown of the Sentinel POC environment..."

# Stop containers and remove networks, volumes, and orphan containers
docker compose down --volumes --remove-orphans

echo "Teardown complete. All containers, networks, and Neo4j volumes are destroyed."
