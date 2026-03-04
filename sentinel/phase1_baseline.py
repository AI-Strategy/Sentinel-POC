# sentinel/phase1_baseline.py
# ---------------------------
# "The Walking Skeleton" — Phase 1 Reference Implementation.
# Captures the foundational Ghost Invoice reconciliation logic.
#
# Module 1: Ingestor (JSON, CSV, XML)
# Module 2: EntityMapper (Gemini Batch Mapping)
# Module 3: GraphEngine (Neo4j Batch Load & Reconciliation)
# Module 4: Reporter (Orchestrator)

import json
import csv
import xml.etree.ElementTree as ET
import os
import logging
from neo4j import GraphDatabase
from google import genai
from google.genai import types

# Configure logging for standalone execution
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("sentinel.phase1")

# ==========================================
# MODULE 1: INGESTOR
# ==========================================
class Ingestor:
    @staticmethod
    def ingest_invoice(filepath: str) -> list[dict]:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted JSON in {filepath}. Error: {e}")

    @staticmethod
    def ingest_po(filepath: str) -> list[dict]:
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except Exception as e:
            raise ValueError(f"Failed to read CSV in {filepath}. Error: {e}")

    @staticmethod
    def ingest_pod(filepath: str) -> list[dict]:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            pods = []
            for item in root.findall('waybill'):
                pods.append({
                    "waybill_ref": item.find('waybill_ref').text,
                    "qty_received_at_dock": int(item.find('qty_received_at_dock').text),
                    "part_id": item.find('part_id').text,
                    "condition": item.find('condition').text
                })
            return pods
        except ET.ParseError as e:
            raise ValueError(f"Corrupted XML in {filepath}. Error: {e}")

# ==========================================
# MODULE 2: LOGIC ENGINE (LLM MAPPER)
# ==========================================
class EntityMapper:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_mapping(self, invoices: list, pos: list, pods: list) -> dict:
        """
        Uses Gemini 2.5 Flash to resolve disparate identifiers into a canonical ID.
        Strictly replaces fragile Regex matching.
        """
        skus = list(set([i['sku'] for i in invoices]))
        item_refs = list(set([p['item_reference'] for p in pos]))
        part_ids = list(set([d['part_id'] for d in pods]))

        prompt = f"""
        Map the following disparate inventory identifiers to a single canonical ID based on semantic similarity.
        SKUs: {skus}
        Item References: {item_refs}
        Part IDs: {part_ids}
        
        Return ONLY a JSON dictionary where keys are the raw identifiers (SKU, Item Ref, or Part ID) and values are a unified canonical string name. 
        Example: {{"SKU-123-BLK": "WIDGET_A", "REF_WIDGET_A": "WIDGET_A"}}
        """

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)

# ==========================================
# MODULE 3: GRAPH ENGINE
# ==========================================
class GraphEngine:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def load_data(self, invoices, pos, pods, mapping):
        """
        Uses UNWIND for batch processing to guarantee sub-10s execution for 10k+ rows.
        """
        with self.driver.session() as session:
            # Load Invoices
            session.run("""
                UNWIND $invoices AS inv
                MERGE (t:Transaction {canonical_id: $mapping[inv.sku]})
                CREATE (i:InvoiceLine {
                    invoice_id: inv.invoice_id, 
                    sku: inv.sku, 
                    qty: toFloat(inv.quantity), 
                    price: toFloat(inv.billed_unit_price)
                })
                CREATE (i)-[:MAPS_TO]->(t)
            """, invoices=invoices, mapping=mapping)

            # Load Purchase Orders
            session.run("""
                UNWIND $pos AS po
                MERGE (t:Transaction {canonical_id: $mapping[po.item_reference]})
                CREATE (p:POLine {
                    po_id: po.PO_id, 
                    item_ref: po.item_reference, 
                    qty: toFloat(po.qty_authorized), 
                    price: toFloat(po.agreed_unit_price)
                })
                CREATE (p)-[:MAPS_TO]->(t)
            """, pos=pos, mapping=mapping)

            # Load Proof of Delivery
            session.run("""
                UNWIND $pods AS pod
                MERGE (t:Transaction {canonical_id: $mapping[pod.part_id]})
                CREATE (d:PODLine {
                    waybill_ref: pod.waybill_ref, 
                    part_id: pod.part_id, 
                    qty: toFloat(pod.qty_received_at_dock)
                })
                CREATE (d)-[:MAPS_TO]->(t)
            """, pods=pods, mapping=mapping)

    def run_reconciliation(self) -> dict:
        report = {"leaks": [], "total_recoverable_amount": 0.0}
        with self.driver.session() as session:
            # 1. Price Variance
            price_variance = session.run("""
                MATCH (inv:InvoiceLine)-[:MAPS_TO]->(t:Transaction)<-[:MAPS_TO]-(po:POLine)
                WHERE inv.price > po.price
                RETURN inv.invoice_id AS invoice, inv.sku AS item, inv.price AS billed, po.price AS contracted, inv.qty AS qty
            """)
            for record in price_variance:
                variance = (record["billed"] - record["contracted"]) * record["qty"]
                report["total_recoverable_amount"] += variance
                report["leaks"].append({
                    "type": "Price Variance",
                    "evidence": f"Invoice {record['invoice']} billed at {record['billed']}, PO contracted at {record['contracted']}.",
                    "recoverable": variance
                })

            # 2. Quantity Mismatch
            qty_mismatch = session.run("""
                MATCH (inv:InvoiceLine)-[:MAPS_TO]->(t:Transaction)<-[:MAPS_TO]-(pod:PODLine)
                WHERE inv.qty > pod.qty
                MATCH (inv)-[:MAPS_TO]->(t)<-[:MAPS_TO]-(po:POLine)
                RETURN inv.invoice_id AS invoice, inv.qty AS billed_qty, pod.qty AS received_qty, po.price AS unit_price
            """)
            for record in qty_mismatch:
                variance = (record["billed_qty"] - record["received_qty"]) * record["unit_price"]
                report["total_recoverable_amount"] += variance
                report["leaks"].append({
                    "type": "Quantity Mismatch",
                    "evidence": f"Invoice {record['invoice']} billed for {record['billed_qty']}, but only {record['received_qty']} received at dock.",
                    "recoverable": variance
                })

            # 3. Phantom Line
            phantom_lines = session.run("""
                MATCH (inv:InvoiceLine)-[:MAPS_TO]->(t:Transaction)
                WHERE NOT (t)<-[:MAPS_TO]-(:POLine) AND NOT (t)<-[:MAPS_TO]-(:PODLine)
                RETURN inv.invoice_id AS invoice, inv.sku AS item, (inv.qty * inv.price) AS total_billed
            """)
            for record in phantom_lines:
                report["total_recoverable_amount"] += record["total_billed"]
                report["leaks"].append({
                    "type": "Phantom Line",
                    "evidence": f"Invoice {record['invoice']} contains item {record['item']} with no corresponding PO or POD.",
                    "recoverable": record["total_billed"]
                })

        return report

# ==========================================
# MODULE 4: REPORTER (ORCHESTRATOR)
# ==========================================
def generate_evidence_package(invoice_file="invoice.json", po_file="po.csv", pod_file="pod.xml"):
    # 1. Ingest
    invoices = Ingestor.ingest_invoice(invoice_file)
    pos = Ingestor.ingest_po(po_file)
    pods = Ingestor.ingest_pod(pod_file)

    # 2. Map (LLM)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        return

    mapper = EntityMapper(api_key=api_key)
    mapping_dict = mapper.generate_mapping(invoices, pos, pods)

    # 3. Graph Execution
    graph = GraphEngine(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        os.getenv("NEO4J_USER", "neo4j"),
        os.getenv("NEO4J_PASS", "password")
    )
    graph.clear_database()
    graph.load_data(invoices, pos, pods, mapping_dict)
    
    # 4. Reconcile & Report
    report = graph.run_reconciliation()
    graph.close()

    # Output Evidence
    report_file = "reconciliation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=4)
    logger.info("Traceability Report Generated: %s", report_file)

if __name__ == "__main__":
    # Example execution (dummy call)
    logger.info("Sentinel Phase 1 Baseline Engine initialised.")
    # generate_evidence_package()
