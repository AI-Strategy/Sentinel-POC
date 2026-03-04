"""
sentinel/tests/test_unit.py
---------------------------
Atomic unit tests for the LLM matching and NLQ Cypher generation modules.
Utilizes pytest-mock to isolate tests from the Gemini API and Neo4j database.
"""

import pytest
from sentinel.core.match import _llm_match
from sentinel.core.nlq import TextToCypherEngine

pytestmark = pytest.mark.unit

def test_llm_match_success(mocker):
    """Validates that _llm_match correctly parses a valid Gemini JSON response."""
    mock_client = mocker.Mock()
    mock_response = mocker.Mock()
    mock_response.text = '{"matched_key": "PO-SKU-1", "confidence": 0.92, "reason": "Semantic similarity."}'
    mock_client.models.generate_content.return_value = mock_response
    # Mock complete_json instead since _llm_match calls complete_json
    mock_client.complete_json.return_value = {"matched_key": "PO-SKU-1", "confidence": 0.92, "reason": "Semantic similarity."}

    candidates = [{"key": "PO-SKU-1", "description": "Widget A"}]
    key, conf = _llm_match("INV-SKU-1", "Widget Type A", candidates, mock_client)

    assert key == "PO-SKU-1"
    assert conf == 0.92
    mock_client.complete_json.assert_called_once()

def test_llm_match_failure(mocker):
    """Validates that _llm_match degrades gracefully upon an API or JSON parsing exception."""
    mock_client = mocker.Mock()
    mock_client.complete_json.side_effect = Exception("API Timeout")

    candidates = [{"key": "PO-SKU-1", "description": "Widget A"}]
    key, conf = _llm_match("INV-SKU-1", "Widget Type A", candidates, mock_client)

    assert key is None
    assert conf == 0.0
    mock_client.complete_json.assert_called_once()

def test_nlq_engine_generation(mocker):
    """Validates the TextToCypherEngine translates natural language to Cypher without executing it."""
    mocker.patch("sentinel.core.nlq.GraphDatabase.driver")
    # Mock get_client to return a mock client
    mock_client = mocker.Mock()
    mock_client.available = True
    
    engine = TextToCypherEngine("bolt://fake", "user", "pass", client=mock_client)
    
    mock_client.complete.return_value = "MATCH (n:GhostFlag) RETURN n"

    cypher = engine.generate_cypher("Show all ghost flags")
    
    assert cypher == "MATCH (n:GhostFlag) RETURN n"
    engine.close()

def test_nlq_engine_execution_success(mocker):
    """Validates the TextToCypherEngine executes the generated Cypher via a read transaction."""
    mocker.patch("sentinel.core.nlq.GraphDatabase.driver")
    mock_client = mocker.Mock()
    mock_client.available = True
    mock_client.complete.return_value = "MATCH (n) RETURN n"
    
    engine = TextToCypherEngine("bolt://fake", "user", "pass", client=mock_client)

    # Mock Neo4j Session and execute_read
    mock_session_context = mocker.MagicMock()
    mock_session = mocker.MagicMock()
    mock_session.execute_read.return_value = [{"n": "node_data"}]
    mock_session_context.__enter__.return_value = mock_session
    engine.driver.session.return_value = mock_session_context

    result = engine.execute_query("Get nodes")
    
    assert result["error"] is None
    assert result["cypher"] == "MATCH (n) RETURN n"
    assert result["results"] == [{"n": "node_data"}]
    engine.close()

def test_nlq_engine_execution_failure(mocker):
    """Validates the TextToCypherEngine traps database execution exceptions."""
    mocker.patch("sentinel.core.nlq.GraphDatabase.driver")
    mock_client = mocker.Mock()
    mock_client.available = True
    mock_client.complete.return_value = "MATCH (n) RETURN n"
    
    engine = TextToCypherEngine("bolt://fake", "user", "pass", client=mock_client)

    mock_session_context = mocker.MagicMock()
    mock_session = mocker.MagicMock()
    mock_session.execute_read.side_effect = Exception("Database Offline")
    mock_session_context.__enter__.return_value = mock_session
    engine.driver.session.return_value = mock_session_context

    result = engine.execute_query("Get nodes")
    
    assert result["error"] == "Database Offline"
    assert result["results"] == []
    engine.close()
