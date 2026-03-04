# sentinel_poc/Makefile
# Operational management for the Sentinel Liquid Enterprise OS (Phase 1 & Phase 2 POC)
# Version Control: v1.3 - Integrated Steel Thread propagation targets.

.PHONY: install up down test test-unit test-integration run-batch e2e clean serve help propagate-demo

# ── Variables ──────────────────────────────────────────────────────────────────
PYTHON       := python
PIP          := pip
VENV         := venv
REPORTS_DIR  := output/reports
BATCH_DATA   := data/sentenil_dirty_datasets
API_URL      := http://localhost:8000

# Determine OS for venv path
ifeq ($(OS),Windows_NT)
    VENV_BIN := $(VENV)/Scripts
else
    VENV_BIN := $(VENV)/bin
endif

# ── Setup & Infrastructure ────────────────────────────────────────────────────

install: ## Initialize virtual environment and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/$(PIP) install --upgrade pip
	$(VENV_BIN)/$(PIP) install -r requirements.txt
	@echo "✅ Environment initialized. Run 'source $(VENV_BIN)/activate' to begin."

up: ## Launch orchestrated Docker environment (FastAPI + Neo4j 2026.01.4)
	docker compose up --build -d --wait
	@echo "🚀 Sentinel API: $(API_URL) | Neo4j Browser: http://localhost:7474"

down: ## Stop orchestrated Docker environment
	docker compose down

# ── Development & Execution ───────────────────────────────────────────────────

serve: ## Run FastAPI server in development mode (native)
	$(VENV_BIN)/fastapi dev sentinel/main.py

run-batch: ## Execute configuration-driven reconciliation across all dirty datasets
	$(VENV_BIN)/$(PYTHON) -m sentinel.main --batch-dir $(BATCH_DATA) --reports $(REPORTS_DIR)

persist-graph: ## Execute batch reconciliation and persist results to Neo4j
	$(VENV_BIN)/$(PYTHON) -m sentinel.main --batch-dir $(BATCH_DATA) --reports $(REPORTS_DIR) --persist-neo4j

propagate-demo: ## Demonstrate Phase 2 Milestone 3: Round-Trip Update Propagation
	@echo "Propagating price update for PO-2024-001..."
	curl -X POST $(API_URL)/graph/update-po \
		-H "Content-Type: application/json" \
		-d "{\"po_id\": \"PO-2024-001\", \"item_reference\": \"APX-BOLT-M12\", \"new_price\": 0.75}"
	@echo "\n✅ Graph state updated. Impacted flags re-evaluated."

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Execute full suite with 90% coverage enforcement (pytest.ini)
	$(VENV_BIN)/pytest

test-unit: ## Execute atomic unit tests (mocked Gemini/Neo4j)
	$(VENV_BIN)/pytest tests/test_unit.py -m unit

test-integration: ## Execute integration tests against running containers
	$(VENV_BIN)/pytest tests/test_api.py -m integration

e2e: ## Execute automated end-to-end evaluation (Ingest -> Grade -> Teardown)
	chmod +x run_e2e.sh
	./run_e2e.sh

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean: ## Destroy Docker environment, purge Neo4j volumes, and clean caches
	chmod +x teardown.sh
	./teardown.sh
	rm -rf $(REPORTS_DIR)/*
	rm -rf .pytest_cache
	rm -rf output/coverage_html
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ── Help ──────────────────────────────────────────────────────────────────────

help: ## Display this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
