#!/usr/bin/env bash
# sentinel_poc/run_e2e.sh
# Orchestrates the Sentinel POC launch, batch processing, grading, and teardown.

set -e

# 1. Validate Environment Variables
if [[ -z "${GEMINI_API_KEY}" ]]; then
  echo "ERROR: GEMINI_API_KEY environment variable is not set."
  exit 1
fi

# 2. Initialize Docker Environment
echo "Initializing Docker environment (Substrates: Postgres + Neo4j)..."
docker compose up --build --wait

# 3. Execute Batch Pipeline
echo "Executing Sentinel pipeline against dataset batches..."
# Ensure venv is activated if it exists locally
if [ -d "venv" ]; then
  source venv/bin/activate
fi

python sentinel/main.py \
  --batch-dir data/sentenil_dirty_datasets \
  --reports output/reports \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-pass sentinel_neo4j

# 4. Execute Grading Harness
echo "Executing external grading harness..."
python tests/grader.py \
  --datasets data/sentenil_dirty_datasets \
  --reports output/reports \
  --out output/

# 5. Teardown Environment
echo "Executing teardown sequence..."
./teardown.sh

echo "End-to-end evaluation complete. Review grade_summary.md in the output/ directory."
