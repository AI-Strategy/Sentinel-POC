"""
sentinel/core/graph.py  (v0.3)
-------------------------------
Persists ENTITIES and RELATIONS from entity_extractor.py into Neo4j.

Node labels:
  (:Vendor    {vendor_id, name, name_variants, confidence})
  (:Item      {item_id, sku, description, unit, category})
  (:Invoice   {invoice_id, vendor_id, date, currency})
  (:InvoiceLine {line_id, invoice_id, item_id, sku, qty, unit_price, total})
  (:PurchaseOrder {po_id, item_id, agreed_price, qty_authorized, status, currency})
  (:Delivery  {waybill_ref, item_id, qty_received, condition, delivery_date})
  (:Anomaly   {anomaly_id, type, description, severity})
  (:SourceDocument {doc_id, source_file, document_type})

Relationship types (from extraction "relations" array + inferred):
  (Invoice)-[:ISSUED_BY]->(Vendor)
  (Invoice)-[:HAS_LINE]->(InvoiceLine)
  (InvoiceLine)-[:COVERS_ITEM]->(Item)
  (PurchaseOrder)-[:AUTHORISES]->(Item)
  (Delivery)-[:CONFIRMS_ITEM]->(Item)
  (Anomaly)-[:FLAGS]->(InvoiceLine)
  + any custom relations emitted by Gemini extraction
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from neo4j import GraphDatabase, Driver, AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger(__name__)


def _make_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def _uid(*parts: Any) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


# ══════════════════════════════════════════════════════════════════════════════
# PRIMARY: persist extraction envelope from entity_extractor.py
# ══════════════════════════════════════════════════════════════════════════════

def persist_extraction(
    extraction: dict,
    uri:      str = "bolt://localhost:7687",
    user:     str = "neo4j",
    password: str = "password",
):
    """Write a full extraction envelope to Neo4j."""
    driver = _make_driver(uri, user, password)
    eid    = extraction.get("extraction_id", "unknown")
    ents   = extraction.get("entities", {})
    rels   = extraction.get("relations", [])
    anoms  = extraction.get("anomalies", [])

    try:
        with driver.session() as session:
            session.execute_write(_write_vendors,    ents.get("vendors", []))
            session.execute_write(_write_items,      ents.get("items", []))
            session.execute_write(_write_invoices,   ents.get("invoices", []))
            session.execute_write(_write_pos,        ents.get("purchase_orders", []))
            session.execute_write(_write_deliveries, ents.get("deliveries", []))
            session.execute_write(_write_relations,  rels)
            session.execute_write(_write_anomalies,  anoms)
            session.execute_write(
                _write_source_doc,
                extraction.get("extraction_id"),
                extraction.get("source_file", ""),
                extraction.get("document_type", "unknown"),
            )
            
            # Link anomalies to source doc
            if anoms:
                eid = extraction.get("extraction_id")
                def _link_anoms_to_doc(tx):
                    tx.run("""
                        MATCH (a:Anomaly), (s:SourceDocument {doc_id: $doc_id})
                        MERGE (a)-[:EVIDENCE_FROM]->(s)
                    """, doc_id=eid)
                session.execute_write(_link_anoms_to_doc)
        logger.info(
            "Graph extraction %s: %d vendors, %d items, %d invoices, "
            "%d POs, %d deliveries, %d relations, %d anomalies",
            eid,
            len(ents.get("vendors", [])), len(ents.get("items", [])),
            len(ents.get("invoices", [])), len(ents.get("purchase_orders", [])),
            len(ents.get("deliveries", [])), len(rels), len(anoms),
        )
    finally:
        driver.close()


# ── node writers ──────────────────────────────────────────────────────────────

def _write_vendors(tx, vendors: list[dict]):
    for v in vendors:
        tx.run(
            """
            MERGE (n:Vendor {vendor_id: $vendor_id})
            SET n.name          = $name,
                n.name_variants = $name_variants,
                n.confidence    = $confidence
            """,
            vendor_id=v.get("vendor_id", _uid(v.get("name", ""))),
            name=v.get("name", ""),
            name_variants=json.dumps(v.get("name_variants", [])),
            confidence=float(v.get("confidence", 1.0)),
        )


def _write_items(tx, items: list[dict]):
    for item in items:
        tx.run(
            """
            MERGE (n:Item {item_id: $item_id})
            SET n.sku         = $sku,
                n.description = $description,
                n.unit        = $unit,
                n.category    = $category
            """,
            item_id=item.get("item_id", _uid(item.get("sku", ""))),
            sku=item.get("sku", ""),
            description=item.get("description", ""),
            unit=item.get("unit", ""),
            category=item.get("category", ""),
        )


def _write_invoices(tx, invoices: list[dict]):
    for inv in invoices:
        inv_id = inv.get("invoice_id", "")
        tx.run(
            """
            MERGE (i:Invoice {invoice_id: $invoice_id})
            SET i.vendor_id = $vendor_id,
                i.date      = $date,
                i.currency  = $currency
            """,
            invoice_id=inv_id,
            vendor_id=inv.get("vendor_id", ""),
            date=str(inv.get("date", "")),
            currency=inv.get("currency", "USD"),
        )
        if inv.get("vendor_id"):
            tx.run(
                """
                MATCH (i:Invoice {invoice_id: $inv_id})
                MATCH (v:Vendor  {vendor_id:  $vendor_id})
                MERGE (i)-[:ISSUED_BY]->(v)
                """,
                inv_id=inv_id, vendor_id=inv["vendor_id"],
            )
        for li in inv.get("line_items", []):
            line_id = _uid(inv_id, li.get("sku", li.get("item_id", "")))
            tx.run(
                """
                MERGE (l:InvoiceLine {line_id: $line_id})
                SET l.invoice_id  = $invoice_id,
                    l.item_id     = $item_id,
                    l.sku         = $sku,
                    l.qty         = $qty,
                    l.unit_price  = $unit_price,
                    l.total       = $total
                WITH l
                MATCH (i:Invoice {invoice_id: $invoice_id})
                MERGE (i)-[:HAS_LINE]->(l)
                """,
                line_id=line_id, invoice_id=inv_id,
                item_id=li.get("item_id", ""), sku=li.get("sku", ""),
                qty=float(li.get("qty", 0) or 0),
                unit_price=float(li.get("unit_price", 0) or 0),
                total=float(li.get("total", 0) or 0),
            )
            if li.get("item_id"):
                tx.run(
                    """
                    MATCH (l:InvoiceLine {line_id: $line_id})
                    MATCH (it:Item       {item_id: $item_id})
                    MERGE (l)-[:COVERS_ITEM]->(it)
                    """,
                    line_id=line_id, item_id=li["item_id"],
                )


def _write_pos(tx, pos: list[dict]):
    for po in pos:
        tx.run(
            """
            MERGE (p:PurchaseOrder {po_id: $po_id, item_id: $item_id})
            SET p.agreed_price   = $agreed_price,
                p.qty_authorized = $qty_authorized,
                p.status         = $status,
                p.currency       = $currency
            """,
            po_id=po.get("po_id", ""),
            item_id=po.get("item_id", ""),
            agreed_price=float(po.get("agreed_price", 0) or 0),
            qty_authorized=float(po.get("qty_authorized", 0) or 0),
            status=po.get("status", ""),
            currency=po.get("currency", "USD"),
        )
        if po.get("item_id"):
            tx.run(
                """
                MATCH (p:PurchaseOrder {po_id: $po_id, item_id: $item_id})
                MATCH (it:Item         {item_id: $item_id})
                MERGE (p)-[:AUTHORISES]->(it)
                """,
                po_id=po["po_id"], item_id=po["item_id"],
            )


def _write_deliveries(tx, deliveries: list[dict]):
    for d in deliveries:
        tx.run(
            """
            MERGE (d:Delivery {waybill_ref: $waybill_ref, item_id: $item_id})
            SET d.qty_received  = $qty_received,
                d.condition     = $condition,
                d.delivery_date = $delivery_date
            """,
            waybill_ref=d.get("waybill_ref", ""),
            item_id=d.get("item_id", ""),
            qty_received=float(d.get("qty_received", 0) or 0),
            condition=d.get("condition", ""),
            delivery_date=str(d.get("delivery_date", "") or ""),
        )
        if d.get("item_id"):
            tx.run(
                """
                MATCH (del:Delivery {waybill_ref: $waybill_ref, item_id: $item_id})
                MATCH (it:Item      {item_id: $item_id})
                MERGE (del)-[:CONFIRMS_ITEM]->(it)
                """,
                waybill_ref=d["waybill_ref"], item_id=d["item_id"],
            )


def _write_relations(tx, relations: list[dict]):
    id_field_map = {
        "Vendor": "vendor_id", "Invoice": "invoice_id",
        "InvoiceLine": "line_id", "Item": "item_id",
        "PurchaseOrder": "po_id", "Delivery": "waybill_ref",
        "Anomaly": "anomaly_id",
    }
    for rel in relations:
        from_type = rel.get("from_type", "")
        to_type   = rel.get("to_type", "")
        from_id   = rel.get("from_id", "")
        to_id     = rel.get("to_id", "")
        relation  = rel.get("relation", "RELATED_TO").replace(" ", "_").upper()
        props     = rel.get("properties", {})

        if not (from_type and to_type and from_id and to_id):
            continue

        from_key = id_field_map.get(from_type, "id")
        to_key   = id_field_map.get(to_type, "id")

        try:
            cypher = f"""
                MATCH (a:{from_type} {{{from_key}: $from_id}})
                MATCH (b:{to_type}   {{{to_key}:   $to_id}})
                MERGE (a)-[r:{relation}]->(b)
                SET r += $props
            """
            tx.run(cypher, from_id=from_id, to_id=to_id, props=props)
        except Exception as exc:
            logger.debug("Skipped relation %s->%s [%s]: %s", from_id, to_id, relation, exc)


def _write_anomalies(tx, anomalies: list[dict]):
    for i, anom in enumerate(anomalies):
        anomaly_id = _uid(anom.get("type", ""), anom.get("description", ""), i)
        tx.run(
            """
            MERGE (a:Anomaly {anomaly_id: $anomaly_id})
            SET a.type             = $type,
                a.description      = $description,
                a.severity         = $severity,
                a.financial_impact = $financial_impact,
                a.sku              = $sku,
                a.entity_refs      = $entity_refs
            """,
            anomaly_id=anomaly_id,
            type=anom.get("type", ""),
            description=anom.get("description", ""),
            severity=anom.get("severity", "MEDIUM"),
            financial_impact=float(anom.get("financial_impact", 0.0) or 0.0),
            sku=anom.get("sku", ""),
            entity_refs=json.dumps(anom.get("entity_refs", [])),
        )
        
        # Link to entities
        tx.run("""
            MATCH (a:Anomaly {anomaly_id: $anomaly_id})
            UNWIND $refs AS ref
            MATCH (target:InvoiceLine {sku: ref})
            MERGE (a)-[:FLAGS]->(target)
        """, anomaly_id=anomaly_id, refs=anom.get("entity_refs", []))


def _write_source_doc(tx, extraction_id: str, source_file: str, document_type: str):
    tx.run(
        """
        MERGE (s:SourceDocument {doc_id: $doc_id})
        SET s.source_file   = $source_file,
            s.document_type = $document_type
        """,
        doc_id=extraction_id, source_file=source_file, document_type=document_type,
    )


# ══════════════════════════════════════════════════════════════════════════════
# LEGACY: persist TransactionObject + GhostFlag (backward compat)
# ══════════════════════════════════════════════════════════════════════════════

def persist_to_neo4j(transactions, flags,
                     uri="bolt://localhost:7687", user="neo4j", password="password"):
    """Convert legacy pipeline objects → extraction envelope → Neo4j."""
    vendors_seen = {}
    items, pos, deliveries, anomalies = [], [], [], []
    invoices_map = {}

    for txn in transactions:
        inv  = txn.invoice_line
        v_id = inv.vendor_name.lower().replace(" ", "-").replace(".", "")[:32]
        if v_id not in vendors_seen:
            vendors_seen[v_id] = {"vendor_id": v_id, "name": inv.vendor_name,
                                   "name_variants": [], "confidence": 1.0}
        items.append({"item_id": inv.sku.lower(), "sku": inv.sku,
                      "description": inv.description, "unit": "each", "category": ""})
        if inv.invoice_id not in invoices_map:
            invoices_map[inv.invoice_id] = {"invoice_id": inv.invoice_id,
                                             "vendor_id": v_id, "date": inv.date,
                                             "currency": "USD", "line_items": []}
        invoices_map[inv.invoice_id]["line_items"].append({
            "item_id": inv.sku.lower(), "sku": inv.sku,
            "qty": inv.quantity, "unit_price": inv.billed_unit_price,
            "total": round(inv.quantity * inv.billed_unit_price, 4),
        })
        if txn.po_line:
            po = txn.po_line
            pos.append({"po_id": po.po_id, "item_id": inv.sku.lower(),
                        "agreed_price": po.agreed_unit_price,
                        "qty_authorized": po.qty_authorized,
                        "status": po.status, "currency": "USD"})
        if txn.pod_line:
            d = txn.pod_line
            deliveries.append({"waybill_ref": d.waybill_ref, "item_id": inv.sku.lower(),
                                "qty_received": d.qty_received_at_dock,
                                "condition": d.condition, "delivery_date": None})



    for flag_obj in flags:
        anomalies.append({
            "type": flag_obj.ghost_type.value,
            "description": flag_obj.narrative,
            "severity": flag_obj.severity,
            "financial_impact": flag_obj.financial_impact,
            "sku": flag_obj.sku,
            "entity_refs": [flag_obj.sku, flag_obj.invoice_id]
        })

    extraction = {
        "extraction_id": _uid("legacy", str(len(transactions))),
        "source_file": "legacy_pipeline", "document_type": "combined",
        "extracted_at": "", "used_vision": False,
        "entities": {
            "vendors": list(vendors_seen.values()), "items": items,
            "invoices": list(invoices_map.values()),
            "purchase_orders": pos, "deliveries": deliveries,
        },
        "relations": [], "anomalies": anomalies,
    }
    persist_extraction(extraction, uri=uri, user=user, password=password)


# ══════════════════════════════════════════════════════════════════════════════
# GDS anomaly analysis
# ══════════════════════════════════════════════════════════════════════════════

def run_gds_anomaly_analysis(uri="bolt://localhost:7687", user="neo4j", password="password") -> dict:
    driver  = _make_driver(uri, user, password)
    results = {"degree_centrality": [], "wcc_components": []}
    try:
        with driver.session() as session:
            session.run("""
                CALL gds.graph.project(
                  'sentinel-entity-graph',
                  ['InvoiceLine','Anomaly','Vendor','Item'],
                  { FLAGS:{orientation:'UNDIRECTED'}, COVERS_ITEM:{orientation:'UNDIRECTED'},
                    ISSUED_BY:{orientation:'UNDIRECTED'} }
                )
            """)
            result = session.run("""
                CALL gds.degree.stream('sentinel-entity-graph')
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS node, score
                WHERE node:InvoiceLine OR node:Vendor
                RETURN labels(node)[0] AS label,
                       COALESCE(node.sku, node.name) AS name, score AS connections
                ORDER BY score DESC LIMIT 15
            """)
            results["degree_centrality"] = [dict(r) for r in result]
            result = session.run("""
                CALL gds.wcc.stream('sentinel-entity-graph')
                YIELD nodeId, componentId
                WITH componentId, count(*) AS size
                RETURN componentId, size ORDER BY size DESC LIMIT 10
            """)
            results["wcc_components"] = [dict(r) for r in result]
            session.run("CALL gds.graph.drop('sentinel-entity-graph')")
    except Exception as exc:
        logger.warning("GDS analysis failed: %s", exc)
        results["gds_error"] = str(exc)
    finally:
        driver.close()
    return results
# ══════════════════════════════════════════════════════════════════════════════
# Dashboard Metrics (Executive analytics — Asynchronous)
# ══════════════════════════════════════════════════════════════════════════════

async def get_dashboard_metrics_async(uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "sentinel_neo4j") -> dict:
    """
    Executes the executive analytics layer asynchronously.
    Returns a compiled JSON payload of financial risk and performance metrics.
    """
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    metrics = {}
    try:
        async with driver.session() as session:
            async def _vendor_exposure(tx):
                res = await tx.run("""
                    MATCH (v:Vendor)<-[:ISSUED_BY]-(i:Invoice)-[:HAS_LINE]->(l:InvoiceLine)<-[:FLAGS]-(a:Anomaly)
                    RETURN 
                        v.name AS Vendor, 
                        count(DISTINCT i.invoice_id) AS ImpactedInvoices,
                        count(a) AS TotalAnomalies,
                        sum(a.financial_impact) AS TotalFinancialExposureUSD
                    ORDER BY TotalFinancialExposureUSD DESC LIMIT 10
                """)
                return [dict(r) for r in await res.data()]
            metrics["exposure_by_vendor"] = await session.execute_read(_vendor_exposure)

            # 2. Leakage Distribution by Ghost Type
            async def _leakage_type(tx):
                res = await tx.run("""
                    MATCH (a:Anomaly)
                    RETURN 
                        a.type AS LeakageCategory, 
                        count(a) AS IncidentCount, 
                        sum(a.financial_impact) AS TotalValueUSD
                    ORDER BY TotalValueUSD DESC
                """)
                return [dict(r) for r in await res.data()]
            metrics["leakage_by_type"] = await session.execute_read(_leakage_type)

            # 3. Highest Risk SKUs
            async def _highest_risk_skus(tx):
                res = await tx.run("""
                    MATCH (a:Anomaly)-[:FLAGS]->(l:InvoiceLine)
                    RETURN 
                        l.sku AS SKU, 
                        l.description AS Description, 
                        count(a) AS FlagCount, 
                        sum(a.financial_impact) AS SKUExposureUSD
                    ORDER BY SKUExposureUSD DESC LIMIT 10
                """)
                return [dict(r) for r in await res.data()]
            metrics["highest_risk_skus"] = await session.execute_read(_highest_risk_skus)

            # 4. LLM vs Exact Match Performance
            async def _match_perf(tx):
                res = await tx.run("""
                    MATCH ()-[r:MATCHED_TO_PO]->()
                    RETURN 
                        r.method AS MatchMethod, 
                        count(r) AS ResolutionCount,
                        avg(r.score) AS AverageConfidenceScore
                    ORDER BY ResolutionCount DESC
                """)
                return [dict(r) for r in await res.data()]
            metrics["match_performance"] = await session.execute_read(_match_perf)

            # 5. Phantom Line Audit
            async def _phantom_audit(tx):
                res = await tx.run("""
                    MATCH (a:Anomaly {type: 'PHANTOM_LINE'})-[:FLAGS]->(l:InvoiceLine)<-[:HAS_LINE]-(i:Invoice)
                    MATCH (a)-[:EVIDENCE_FROM]->(s:SourceDocument)
                    RETURN 
                        i.invoice_id AS InvoiceID, 
                        l.sku AS SKU, 
                        a.financial_impact AS CapitalAtRisk, 
                        collect(s.source_file + ' (DocID: ' + s.doc_id + ')') AS EvidencePointers
                    ORDER BY CapitalAtRisk DESC
                """)
                return [dict(r) for r in await res.data()]
            metrics["phantom_line_audit"] = await session.execute_read(_phantom_audit)

    except Exception as exc:
        logger.error("Async Dashboard metrics failed: %s", exc)
        metrics["error"] = str(exc)
    finally:
        await driver.close()
    return metrics


def get_dashboard_metrics(uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "sentinel_neo4j") -> dict:
    # ... legacy sync version if needed ...
    pass
