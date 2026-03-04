"""
sentinel/tests/test_api.py
--------------------------
Integration test suite for the Sentinel Liquid Enterprise OS API.
Validates the FastAPI server and its connection to the Neo4j graph.
Requires the Docker environment to be actively running at localhost:8000.
"""

import pytest
import httpx

# The API is exposed on the host machine at port 8000
BASE_URL = "http://localhost:8000"

# The internal Docker network address for the database container
INTERNAL_NEO4J_URI = "bolt://neo4j:7687"


@pytest.fixture(scope="module")
def client():
    """Provides an HTTPX client for the duration of the test module."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


@pytest.mark.integration
def test_health_check(client):
    """Validates the API boot status and service nomenclature."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sentinel-ghost-invoice-api"


@pytest.mark.integration
@pytest.mark.nlq
def test_query_endpoint(client):
    """Validates the Text-to-Cypher LLM generation and database execution."""
    payload = {
        "question": "How many total anomalies exist in the graph?",
        "neo4j_uri": INTERNAL_NEO4J_URI,
        "neo4j_user": "neo4j",
        "neo4j_pass": "sentinel_neo4j"  # Synchronised with v0.3 Substrate
    }

    response = client.post("/query", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "cypher" in data
    assert "results" in data
    assert data["error"] is None
    assert isinstance(data["results"], list)


@pytest.mark.integration
@pytest.mark.dashboard
def test_dashboard_metrics(client):
    """Validates the concurrent execution of the dashboard Cypher metrics."""
    payload = {
        "neo4j_uri": INTERNAL_NEO4J_URI,
        "neo4j_user": "neo4j",
        "neo4j_pass": "sentinel_neo4j"  # Synchronised with v0.3 Substrate
    }
    
    response = client.post("/dashboard/metrics", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    expected_keys = [
        "financial_exposure_by_vendor",
        "leakage_distribution_by_type",
        "highest_risk_skus",
        "llm_vs_exact_match_performance",
        "phantom_line_audit_trail"
    ]
    
    for key in expected_keys:
        assert key in data
        assert isinstance(data[key], list)
