"""
sentinel/core/nlq.py
--------------------
Natural Language to Cypher execution engine (v1.0 — Gemini).
Translates human questions into read-only Neo4j queries using the unified GeminiClient.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver
from .llm import get_client

logger = logging.getLogger(__name__)

# Grounding schema for Gemini to ensure Cypher accuracy (V0.3 Schema)
GRAPH_SCHEMA = """
Nodes and Properties:
- (:Vendor {vendor_id: STRING, name: STRING, name_variants: JSON_STRING, confidence: FLOAT})
- (:Item {item_id: STRING, sku: STRING, description: STRING, unit: STRING, category: STRING})
- (:Invoice {invoice_id: STRING, vendor_id: STRING, date: STRING, currency: STRING})
- (:InvoiceLine {line_id: STRING, invoice_id: STRING, item_id: STRING, sku: STRING, qty: FLOAT, unit_price: FLOAT, total: FLOAT})
- (:PurchaseOrder {po_id: STRING, item_id: STRING, agreed_price: FLOAT, qty_authorized: FLOAT, status: STRING, currency: STRING})
- (:Delivery {waybill_ref: STRING, item_id: STRING, qty_received: FLOAT, condition: STRING, delivery_date: STRING})
- (:Anomaly {anomaly_id: STRING, type: STRING, description: STRING, severity: STRING, entity_refs: JSON_STRING})
- (:SourceDocument {doc_id: STRING, source_file: STRING, document_type: STRING})

Relationships:
- (Invoice)-[:ISSUED_BY]->(Vendor)
- (Invoice)-[:HAS_LINE]->(InvoiceLine)
- (InvoiceLine)-[:COVERS_ITEM]->(Item)
- (PurchaseOrder)-[:AUTHORISES]->(Item)
- (Delivery)-[:CONFIRMS_ITEM]->(Item)
- (Anomaly)-[:FLAGS]->(InvoiceLine)

Anomaly Types:
- "PRICE_VARIANCE"
- "QTY_MISMATCH"
- "PHANTOM_LINE"
"""

class TextToCypherEngine:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_pass: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

    def close(self):
        self.driver.close()

    def generate_cypher(self, question: str) -> str:
        """Translates a natural language question into a Cypher query."""
        client = get_client()
        if not client.available:
            raise RuntimeError("Gemini client unavailable — check GEMINI_API_KEY.")

        prompt = f"""
        You are an expert Neo4j Cypher developer for a procurement forensic system called Sentinel.
        
        Given the following Neo4j graph schema (v0.3):
        {GRAPH_SCHEMA}
        
        Translate the following question into a valid, optimized Cypher query:
        "{question}"
        
        Rules:
        1. Return ONLY the raw Cypher query string.
        2. Do NOT include markdown fences, backticks, or commentary.
        3. Ensure the query is strictly READ-ONLY (MATCH, RETURN, WITH, UNWIND, etc.).
        4. Do NOT use mutating operations (MERGE, CREATE, SET, DELETE, CALL etc.).
        5. If the question asks about 'anomalies', use the (:Anomaly) node.
        6. For vendor lookups, use the 'name' property on (:Vendor).
        """
        
        response = client.complete(prompt, max_tokens=1024)
        
        # Strip potential markdown fences if the LLM ignores the strict output rule
        cypher = response.replace("```cypher", "").replace("```", "").strip()
        logger.debug("Generated Cypher: %s", cypher)
        return cypher

    def execute_query(self, question: str) -> Dict[str, Any]:
        """Generates Cypher from text and executes it against Neo4j securely."""
        cypher_query = self.generate_cypher(question)
        
        try:
            with self.driver.session() as session:
                # Enforce read-only execution at the neo4j session level
                result = session.execute_read(self._run_transaction, cypher_query)
                return {
                    "question": question,
                    "cypher": cypher_query,
                    "results": result,
                    "error": None
                }
        except Exception as e:
            logger.error("Failed to execute NLQ: %s", str(e))
            return {
                "question": question,
                "cypher": cypher_query,
                "results": [],
                "error": str(e)
            }

    @staticmethod
    def _run_transaction(tx, query: str) -> List[Dict[str, Any]]:
        result = tx.run(query)
        return [dict(record) for record in result]
