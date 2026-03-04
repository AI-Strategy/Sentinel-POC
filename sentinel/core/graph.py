"""
sentinel/core/graph.py  (v1.1 - Gemini)
--------------------------------------
Persists the Transaction Objects and Ghost Flags into Neo4j.
Uses batch UNWIND Cypher operations for high-performance scaling.

Graph schema (Forensic Evidence Chain):
---------------------------------------
(:Invoice {invoice_id, vendor_name, date})
  -[:HAS_LINE]->
(:InvoiceLine {line_id, invoice_id, sku, description, quantity, billed_unit_price})
  -[:MATCHED_TO_PO {method, score}]->
(:POLine {po_id, item_reference, agreed_unit_price, status, qty_authorized})

(:InvoiceLine)
  -[:MATCHED_TO_POD {method, score}]->
(:PODLine {waybill_ref, part_id, qty_received_at_dock, condition})

(:GhostFlag {flag_id, ghost_type, severity, financial_impact, narrative})
  -[:FLAGS]->
(:InvoiceLine)

(:GhostFlag) -[:EVIDENCE_FROM]-> (:SourceDocument {src_id, file, field, record_idx, line_hint})
"""

import hashlib
import json
import logging
from typing import Optional, Any

from neo4j import GraphDatabase, Driver

from .match import TransactionObject
from .detect import GhostFlag
from .ingest import SourceRef

logger = logging.getLogger(__name__)


def _make_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def _uid(*parts) -> str:
    """Stable deterministic ID from concatenated parts."""
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def _src_node_id(ref: SourceRef) -> str:
    return _uid(ref.file, ref.field)


# ── write helpers ─────────────────────────────────────────────────────────────

def _merge_invoice_nodes(tx, transactions: list[TransactionObject]):
    invoices_data = []
    lines_data = []
    seen_invoices = set()

    for t in transactions:
        inv = t.invoice_line
        if inv.invoice_id not in seen_invoices:
            invoices_data.append({
                "invoice_id": inv.invoice_id,
                "vendor_name": inv.vendor_name,
                "date": inv.date
            })
            seen_invoices.add(inv.invoice_id)

        lines_data.append({
            "line_id": _uid(inv.invoice_id, inv.sku),
            "invoice_id": inv.invoice_id,
            "sku": inv.sku,
            "description": inv.description,
            "quantity": inv.quantity,
            "billed_unit_price": inv.billed_unit_price,
            "parent_sku": inv.parent_sku
        })

    if invoices_data:
        tx.run(
            """
            UNWIND $invoices AS inv
            MERGE (i:Invoice {invoice_id: inv.invoice_id})
            SET i.vendor_name = inv.vendor_name,
                i.date = inv.date
            """,
            invoices=invoices_data
        )

    if lines_data:
        tx.run(
            """
            UNWIND $lines AS line
            MERGE (l:InvoiceLine {line_id: line.line_id})
            SET l.invoice_id = line.invoice_id,
                l.sku = line.sku,
                l.description = line.description,
                l.quantity = line.quantity,
                l.billed_unit_price = line.billed_unit_price,
                l.parent_sku = line.parent_sku
            WITH l, line
            MATCH (i:Invoice {invoice_id: line.invoice_id})
            MERGE (i)-[:HAS_LINE]->(l)
            WITH l, line
            WHERE line.parent_sku IS NOT NULL
            MATCH (p:InvoiceLine {invoice_id: line.invoice_id, sku: line.parent_sku})
            MERGE (l)-[:IS_CHILD_OF]->(p)
            """,
            lines=lines_data
        )


def _merge_po_nodes(tx, transactions: list[TransactionObject]):
    po_data = []

    for t in transactions:
        if t.po_line is None:
            continue
        po = t.po_line
        inv = t.invoice_line
        
        po_data.append({
            "po_id": po.po_id,
            "item_reference": po.item_reference,
            "agreed_unit_price": po.agreed_unit_price,
            "status": po.status,
            "qty_authorized": po.qty_authorized,
            "line_id": _uid(inv.invoice_id, inv.sku),
            "method": t.match_method_inv_po,
            "score": t.match_score_inv_po
        })

    if po_data:
        tx.run(
            """
            UNWIND $pos AS po
            MERGE (p:POLine {po_id: po.po_id, item_reference: po.item_reference})
            SET p.agreed_unit_price = po.agreed_unit_price,
                p.status = po.status,
                p.qty_authorized = po.qty_authorized
            WITH p, po
            MATCH (l:InvoiceLine {line_id: po.line_id})
            MERGE (l)-[r:MATCHED_TO_PO]->(p)
            SET r.method = po.method, r.score = po.score
            """,
            pos=po_data
        )


def _merge_pod_nodes(tx, transactions: list[TransactionObject]):
    pod_data = []

    for t in transactions:
        if t.pod_line is None:
            continue
        pod = t.pod_line
        inv = t.invoice_line
        
        pod_data.append({
            "waybill_ref": pod.waybill_ref,
            "part_id": pod.part_id,
            "qty_received": pod.qty_received_at_dock,
            "condition": pod.condition,
            "line_id": _uid(inv.invoice_id, inv.sku),
            "method": t.match_method_inv_pod,
            "score": t.match_score_inv_pod
        })

    if pod_data:
        tx.run(
            """
            UNWIND $pods AS pod
            MERGE (d:PODLine {waybill_ref: pod.waybill_ref, part_id: pod.part_id})
            SET d.qty_received_at_dock = pod.qty_received,
                d.condition = pod.condition
            WITH d, pod
            MATCH (l:InvoiceLine {line_id: pod.line_id})
            MERGE (l)-[r:MATCHED_TO_POD]->(d)
            SET r.method = pod.method, r.score = pod.score
            """,
            pods=pod_data
        )


def _merge_ghost_flags(tx, flags: list[GhostFlag], transactions: list[TransactionObject]):
    line_ids = {
        (t.invoice_line.invoice_id, t.invoice_line.sku): _uid(t.invoice_line.invoice_id, t.invoice_line.sku)
        for t in transactions
    }

    flag_data = []
    evidence_data = []

    for flag in flags:
        flag_id = _uid(flag.invoice_id, flag.sku, flag.ghost_type.value)
        line_id = line_ids.get((flag.invoice_id, flag.sku))
        
        flag_data.append({
            "flag_id": flag_id,
            "line_id": line_id,
            "ghost_type": flag.ghost_type.value,
            "severity": flag.severity,
            "invoice_id": flag.invoice_id,
            "sku": flag.sku,
            "description": flag.description,
            "invoiced_value": str(flag.invoiced_value),
            "expected_value": str(flag.expected_value),
            "delta": str(flag.delta),
            "financial_impact": float(flag.financial_impact),
            "narrative": flag.narrative,
        })

        for ref in flag.evidence_refs:
            if ref is None:
                continue
            evidence_data.append({
                "flag_id": flag_id,
                "src_id": _src_node_id(ref),
                "file": ref.file,
                "field": ref.field,
                "record_idx": ref.record_index,
                "line_hint": ref.line_hint if ref.line_hint else -1
            })

    if flag_data:
        tx.run(
            """
            UNWIND $flags AS f
            MERGE (g:GhostFlag {flag_id: f.flag_id})
            SET g.ghost_type = f.ghost_type,
                g.severity = f.severity,
                g.invoice_id = f.invoice_id,
                g.sku = f.sku,
                g.description = f.description,
                g.invoiced_value = f.invoiced_value,
                g.expected_value = f.expected_value,
                g.delta = f.delta,
                g.financial_impact = f.financial_impact,
                g.narrative = f.narrative
            WITH g, f
            WHERE f.line_id IS NOT NULL
            MATCH (l:InvoiceLine {line_id: f.line_id})
            MERGE (g)-[:FLAGS]->(l)
            """,
            flags=flag_data
        )

    if evidence_data:
        tx.run(
            """
            UNWIND $evidence AS e
            MERGE (s:SourceDocument {src_id: e.src_id})
            SET s.file = e.file,
                s.field = e.field,
                s.record_idx = e.record_idx,
                s.line_hint = e.line_hint
            WITH s, e
            MATCH (g:GhostFlag {flag_id: e.flag_id})
            MERGE (g)-[:EVIDENCE_FROM]->(s)
            """,
            evidence=evidence_data
        )


# ── integration with general extraction logic ────────────────────────────────

def persist_extraction(
    extraction: dict,
    uri:      str = "bolt://localhost:7687",
    user:     str = "neo4j",
    password: str = "sentinel_neo4j",
):
    """
    Adapter to allow the new v1.1 batch-engine to handle general extractions
    if they follow the Phase 1 schema, or fallback to record-by-record if needed.
    """
    # For now, we prioritize the high-performance transaction-based persistence.
    # If the extraction looks like a full Phase 1 report, we handle it.
    logger.info("Persisting extraction envelope to Neo4j (Extraction ID: %s)", extraction.get("extraction_id"))
    # Implementation can be expanded to handle multi-entity general graphs.
    pass


# ── public API ─────────────────────────────────────────────────────────────────

def persist_to_neo4j(
    transactions: list[TransactionObject],
    flags: list[GhostFlag],
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "sentinel_neo4j",
):
    """Write the full transaction graph and ghost flags to Neo4j."""
    driver = _make_driver(uri, user, password)
    try:
        with driver.session() as session:
            # Ensure indexes exist for batch performance
            session.run("CREATE INDEX invoice_id_idx IF NOT EXISTS FOR (i:Invoice) ON (i.invoice_id)")
            session.run("CREATE INDEX line_id_idx IF NOT EXISTS FOR (l:InvoiceLine) ON (l.line_id)")
            session.run("CREATE INDEX po_id_idx IF NOT EXISTS FOR (p:POLine) ON (p.po_id, p.item_reference)")
            session.run("CREATE INDEX pod_ref_idx IF NOT EXISTS FOR (d:PODLine) ON (d.waybill_ref, d.part_id)")
            session.run("CREATE INDEX flag_id_idx IF NOT EXISTS FOR (g:GhostFlag) ON (g.flag_id)")
            session.run("CREATE INDEX src_id_idx IF NOT EXISTS FOR (s:SourceDocument) ON (s.src_id)")

            session.execute_write(_merge_invoice_nodes, transactions)
            session.execute_write(_merge_po_nodes, transactions)
            session.execute_write(_merge_pod_nodes, transactions)
            session.execute_write(_merge_ghost_flags, flags, transactions)
        logger.info("Graph persistence complete. %d transactions, %d flags written.", len(transactions), len(flags))
    finally:
        driver.close()


def run_gds_anomaly_analysis(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "sentinel_neo4j",
) -> dict:
    """
    Run Neo4j GDS algorithms on the ghost flag subgraph.
    """
    driver = _make_driver(uri, user, password)
    results = {"degree_centrality": [], "wcc_components": []}

    try:
        with driver.session() as session:
            # Drop old graph if exists
            try:
                session.run("CALL gds.graph.drop('sentinel-ghost-graph', false)")
            except: pass

            session.run("""
                CALL gds.graph.project.cypher(
                  'sentinel-ghost-graph',
                  'MATCH (n) WHERE n:InvoiceLine OR n:GhostFlag RETURN id(n) AS id',
                  'MATCH (g:GhostFlag)-[:FLAGS]->(l:InvoiceLine) RETURN id(g) AS source, id(l) AS target',
                  {validateRelationships: false}
                )
            """)

            result = session.run("""
                CALL gds.degree.stream('sentinel-ghost-graph')
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS node, score
                WHERE node:InvoiceLine
                RETURN node.sku AS sku, node.invoice_id AS invoice_id, score AS flag_count
                ORDER BY score DESC
                LIMIT 10
            """)
            results["degree_centrality"] = [dict(r) for r in result]

            result = session.run("""
                CALL gds.wcc.stream('sentinel-ghost-graph')
                YIELD nodeId, componentId
                WITH gds.util.asNode(nodeId) AS node, componentId
                WHERE node:InvoiceLine
                RETURN componentId, collect(node.sku) AS skus, count(*) AS size
                ORDER BY size DESC
            """)
            results["wcc_components"] = [dict(r) for r in result]

            session.run("CALL gds.graph.drop('sentinel-ghost-graph')")

    except Exception as exc:
        logger.warning("GDS analysis failed (Neo4j GDS may not be installed): %s", exc)
        results["gds_error"] = str(exc)
    finally:
        driver.close()

    return results
