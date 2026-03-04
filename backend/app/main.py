import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .core.ingest import Ingestor
from .core.match import EntityMapper
from .core.graph import GraphEngine

load_dotenv()

app = FastAPI(
    title="Sentinel Phase 1: Ghost Invoice Reconciliation",
    description="Liquid Enterprise OS — AI-First Reconciliation Substrate",
    version="1.0.0",
)

DATA_DIR = Path("data")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

class ReconcileRequest(BaseModel):
    clear_existing: bool = True

@app.post("/reconcile", summary="Trigger the full AI-driven reconciliation pipeline")
async def reconcile(req: ReconcileRequest):
    if not GEMINI_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY not configured in substrate.")

    inv_file = DATA_DIR / "invoices.json"
    po_file = DATA_DIR / "purchase_orders.csv"
    pod_file = DATA_DIR / "proof_of_delivery.xml"

    if not all(f.exists() for f in [inv_file, po_file, pod_file]):
        raise HTTPException(status_code=404, detail="One or more data files missing in /data substrate.")

    try:
        # 1. Ingest
        invoices = Ingestor.ingest_invoice(inv_file)
        pos = Ingestor.ingest_po(po_file)
        pods = Ingestor.ingest_pod(pod_file)

        # 2. Map (Gemini Flash)
        mapper = EntityMapper(api_key=GEMINI_KEY)
        mapping_dict = mapper.generate_mapping(invoices, pos, pods)

        # 3. Graph Engine Execution
        graph = GraphEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASS)
        if req.clear_existing:
            graph.clear_database()
        
        graph.load_data(invoices, pos, pods, mapping_dict)
        
        # 4. Reconcile & Report via Cypher
        report = graph.run_reconciliation()
        graph.close()

        # Save result to output for UI/Audit
        output_path = Path("output/reconciliation_report.json")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(json.dumps(report, indent=4))

        return JSONResponse(content=report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel-phase1-api"}
