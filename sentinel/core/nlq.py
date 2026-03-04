"""
sentinel/core/nlq.py (v1.0 — Gemini)
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

# Grounding schema for Gemini to ensure Cypher accuracy (V1.1 Forensic Schema)
GRAPH_SCHEMA = """
Nodes and Properties:
- (:Invoice {invoice_id: STRING, vendor_name: STRING, date: STRING})
- (:InvoiceLine {line_id: STRING, invoice_id: STRING, sku: STRING, description: STRING, quantity: FLOAT, billed_unit_price: FLOAT, parent_sku: STRING})
- (:POLine {po_id: STRING, item_reference: STRING, agreed_unit_price: FLOAT, status: STRING, qty_authorized: FLOAT})
- (:PODLine {waybill_ref: STRING, part_id: STRING, qty_received_at_dock: FLOAT, condition: STRING})
- (:GhostFlag {flag_id: STRING, ghost_type: STRING, severity: STRING, financial_impact: FLOAT, narrative: STRING, invoice_id: STRING, sku: STRING})
- (:SourceDocument {src_id: STRING, file: STRING, field: STRING, record_idx: INTEGER, line_hint: INTEGER})

Relationships:
- (:Invoice)-[:HAS_LINE]->(:InvoiceLine)
- (:InvoiceLine)-[:IS_CHILD_OF]->(:InvoiceLine)
- (:InvoiceLine)-[:MATCHED_TO_PO {method: STRING, score: FLOAT}]->(:POLine)
- (:InvoiceLine)-[:MATCHED_TO_POD {method: STRING, score: FLOAT}]->(:PODLine)
- (:GhostFlag)-[:FLAGS]->(:InvoiceLine)
- (:GhostFlag)-[:EVIDENCE_FROM]->(:SourceDocument)

Ghost Types (ghost_type property):
- "PRICE_VARIANCE"
- "QTY_MISMATCH"
- "PHANTOM_LINE"

Severity Levels (severity property):
- "HIGH"
- "MEDIUM"
- "LOW"
"""

class TextToCypherEngine:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_pass: str, client: Optional[Any] = None):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        self.client = client or get_client()

    def close(self):
        self.driver.close()

    def generate_cypher(self, question: str) -> str:
        """Translates a natural language question into a Cypher query."""
        if not self.client or not self.client.available:
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
        5. If the question asks about 'anomalies' or 'leaks', use the (:GhostFlag) node.
        6. For vendor info, use the 'vendor_name' property on (:Invoice).
        """
        
        response = self.client.complete(prompt, max_tokens=1024)
        
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
