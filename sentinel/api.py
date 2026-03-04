"""
sentinel/api.py
---------------
FastAPI wrapper around the Sentinel pipeline.
Exposes REST endpoints for integration with the Liquid Enterprise OS.

Endpoints
---------
POST /reconcile          — run the full pipeline, return JSON report
GET  /report/latest      — fetch the most recent report from disk
POST /reconcile/upload   — upload files directly via multipart
POST /query              — execute Natural Language Query against the graph
POST /dashboard/metrics  — execute Cypher analytics dashboard queries asynchronously
"""

import json
import tempfile
import asyncio
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from neo4j import AsyncGraphDatabase

app = FastAPI(
    title="Sentinel Ghost Invoice Reconciliation API",
    description="Liquid Enterprise OS — Phase 1 Walking Skeleton",
    version="0.1.0",
)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Schemas ────────────────────────────────────────────────────────────────────

class ReconcileRequest(BaseModel):
    invoice_path: str = "data/invoices.json"
    po_path:      str = "data/purchase_orders.csv"
    pod_path:     str = "data/proof_of_delivery.xml"
    use_llm:      bool = True
    persist_neo4j: bool = False
    neo4j_uri:    str = "bolt://localhost:7687"
    neo4j_user:   str = "neo4j"
    neo4j_pass:   str = "password"

class NLQRequest(BaseModel):
    question: str
    neo4j_uri:    str = "bolt://localhost:7687"
    neo4j_user:   str = "neo4j"
    neo4j_pass:   str = "password"

class DashboardRequest(BaseModel):
    neo4j_uri:    str = "bolt://localhost:7687"
    neo4j_user:   str = "neo4j"
    neo4j_pass:   str = "password"

class POUpdateRequest(BaseModel):
    po_id: str
    item_reference: str
    new_price: float
    neo4j_uri:    str = "bolt://localhost:7687"
    neo4j_user:   str = "neo4j"
    neo4j_pass:   str = "password"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run_pipeline(
    invoice_path: str,
    po_path: str,
    pod_path: str,
    use_llm: bool = True,
    persist_neo4j: bool = False,
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_pass: str = "password",
) -> dict:
    from core.ingest import load_invoices, load_purchase_orders, load_pod
    from core.match import link_transactions
    from core.detect import detect_ghosts
    from core.report import build_json_report, write_reports

    invoices     = load_invoices(invoice_path)
    pos          = load_purchase_orders(po_path)
    pods         = load_pod(pod_path)
    transactions = link_transactions(invoices, pos, pods, use_llm=use_llm)
    flags        = detect_ghosts(transactions)

    write_reports(flags, transactions, output_dir=OUTPUT_DIR)

    if persist_neo4j:
        from core.graph import persist_to_neo4j
        persist_to_neo4j(transactions, flags, uri=neo4j_uri, user=neo4j_user, password=neo4j_pass)

    return build_json_report(flags, transactions)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.post("/reconcile", summary="Run full Ghost Invoice reconciliation")
async def reconcile(req: ReconcileRequest):
    try:
        report = _run_pipeline(
            invoice_path=req.invoice_path,
            po_path=req.po_path,
            pod_path=req.pod_path,
            use_llm=req.use_llm,
            persist_neo4j=req.persist_neo4j,
            neo4j_uri=req.neo4j_uri,
            neo4j_user=req.neo4j_user,
            neo4j_pass=req.neo4j_pass,
        )
        return JSONResponse(content=report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/reconcile/upload", summary="Upload raw files and run reconciliation")
async def reconcile_upload(
    invoice_file: UploadFile = File(...),
    po_file:      UploadFile = File(...),
    pod_file:     UploadFile = File(...),
    use_llm:      bool = True,
):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        inv_path = tmp / "invoices.json"
        po_path  = tmp / "purchase_orders.csv"
        pod_path = tmp / "proof_of_delivery.xml"

        inv_path.write_bytes(await invoice_file.read())
        po_path.write_bytes(await po_file.read())
        pod_path.write_bytes(await pod_file.read())

        try:
            report = _run_pipeline(
                invoice_path=str(inv_path),
                po_path=str(po_path),
                pod_path=str(pod_path),
                use_llm=use_llm,
            )
            return JSONResponse(content=report)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))


@app.get("/report/latest", summary="Fetch the most recent JSON report")
async def get_latest_report():
    report_path = OUTPUT_DIR / "sentinel_report.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="No report found. Run /reconcile first.")
    return JSONResponse(content=json.loads(report_path.read_text()))


@app.get("/report/latest/markdown", summary="Fetch the most recent Markdown report")
async def get_latest_markdown():
    md_path = OUTPUT_DIR / "sentinel_report.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="No report found. Run /reconcile first.")
    return PlainTextResponse(content=md_path.read_text())


@app.post("/query", summary="Execute Natural Language Query against the graph")
async def ask_graph(req: NLQRequest):
    from core.nlq import TextToCypherEngine
    engine = TextToCypherEngine(req.neo4j_uri, req.neo4j_user, req.neo4j_pass)
    
    try:
        response = engine.execute_query(req.question)
        if response["error"]:
            raise HTTPException(status_code=400, detail=response["error"])
        return JSONResponse(content=response)
    finally:
        engine.close()


@app.post("/dashboard/metrics", summary="Execute Cypher analytics dashboard queries asynchronously")
async def dashboard_metrics(req: DashboardRequest):
    driver = AsyncGraphDatabase.driver(req.neo4j_uri, auth=(req.neo4j_user, req.neo4j_pass))
    
    queries = {
        "financial_exposure_by_vendor": """
            MATCH (i:Invoice)-[:HAS_LINE]->(l:InvoiceLine)<-[:FLAGS]-(g:GhostFlag)
            RETURN 
                i.vendor_name AS Vendor, 
                count(DISTINCT i.invoice_id) AS ImpactedInvoices,
                count(g) AS TotalAnomalies,
                sum(g.financial_impact) AS TotalFinancialExposureUSD
            ORDER BY 
                TotalFinancialExposureUSD DESC
            LIMIT 10;
        """,
        "leakage_distribution_by_type": """
            MATCH (g:GhostFlag)
            RETURN 
                g.ghost_type AS LeakageCategory, 
                count(g) AS IncidentCount, 
                sum(g.financial_impact) AS TotalValueUSD
            ORDER BY 
                TotalValueUSD DESC;
        """,
        "highest_risk_skus": """
            MATCH (g:GhostFlag)
            RETURN 
                g.sku AS SKU, 
                g.description AS Description, 
                count(g) AS FlagCount, 
                sum(g.financial_impact) AS SKUExposureUSD
            ORDER BY 
                SKUExposureUSD DESC
            LIMIT 10;
        """,
        "llm_vs_exact_match_performance": """
            MATCH ()-[r:MATCHED_TO_PO]->()
            RETURN 
                r.method AS MatchMethod, 
                count(r) AS ResolutionCount,
                avg(r.score) AS AverageConfidenceScore
            ORDER BY 
                ResolutionCount DESC;
        """,
        "phantom_line_audit_trail": """
            MATCH (g:GhostFlag {ghost_type: 'PHANTOM_LINE'})-[:EVIDENCE_FROM]->(s:SourceDocument)
            RETURN 
                g.invoice_id AS InvoiceID, 
                g.sku AS SKU, 
                g.financial_impact AS CapitalAtRisk, 
                collect(s.file + ' (Record: ' + toString(s.record_idx) + ')') AS EvidencePointers
            ORDER BY 
                CapitalAtRisk DESC;
        """
    }

    async def run_query(key: str, query: str):
        async with driver.session() as session:
            result = await session.run(query)
            records = await result.data()
            return key, records

    try:
        tasks = [run_query(k, q) for k, q in queries.items()]
        results = await asyncio.gather(*tasks)
        return JSONResponse(content=dict(results))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await driver.close()


@app.post("/graph/update-po", summary="Phase 2: Round-Trip Update Propagation")
async def update_po_price(req: POUpdateRequest):
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(req.neo4j_uri, auth=(req.neo4j_user, req.neo4j_pass))
    try:
        with driver.session() as session:
            session.run("""
                MATCH (p:POLine {po_id: $po_id, item_reference: $item_ref})
                SET p.agreed_unit_price = $price
            """, po_id=req.po_id, item_ref=req.item_reference, price=req.new_price)
            
            # Flush existing flags for this PO
            session.run("""
                MATCH (l:InvoiceLine)-[:MATCHED_TO_PO]->(p:POLine {po_id: $po_id})
                MATCH (l)<-[r:FLAGS]-(g:GhostFlag)
                DETACH DELETE g
            """, po_id=req.po_id)
        return {"status": "success", "message": f"Price updated for {req.po_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel-ghost-invoice-api"}
