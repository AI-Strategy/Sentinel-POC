import logging
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

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
        Loads data with pre-calculated canonical IDs to ensure valid Cypher.
        Uses UNWIND for batch processing performance.
        """
        # Pre-process records with canonical IDs
        prepared_inv = []
        for inv in invoices:
            inv_copy = inv.copy()
            inv_copy['canonical_id'] = mapping.get(inv['sku'], inv['sku'])
            prepared_inv.append(inv_copy)
            
        prepared_po = []
        for po in pos:
            po_copy = po.copy()
            po_copy['canonical_id'] = mapping.get(po['item_reference'], po['item_reference'])
            prepared_po.append(po_copy)
            
        prepared_pod = []
        for pod in pods:
            pod_copy = pod.copy()
            pod_copy['canonical_id'] = mapping.get(pod['part_id'], pod['part_id'])
            prepared_pod.append(pod_copy)

        with self.driver.session() as session:
            # Load Invoices
            session.run("""
                UNWIND $invoices AS inv
                MERGE (t:Transaction {canonical_id: inv.canonical_id})
                CREATE (i:InvoiceLine {
                    invoice_id: inv.invoice_id, 
                    sku: inv.sku, 
                    qty: toFloat(inv.quantity), 
                    price: toFloat(inv.billed_unit_price)
                })
                CREATE (i)-[:MAPS_TO]->(t)
            """, invoices=prepared_inv)

            # Load Purchase Orders
            session.run("""
                UNWIND $pos AS po
                MERGE (t:Transaction {canonical_id: po.canonical_id})
                CREATE (p:POLine {
                    po_id: po.PO_id, 
                    item_ref: po.item_reference, 
                    qty: toFloat(po.qty_authorized), 
                    price: toFloat(po.agreed_unit_price)
                })
                CREATE (p)-[:MAPS_TO]->(t)
            """, pos=prepared_po)

            # Load Proof of Delivery
            session.run("""
                UNWIND $pods AS pod
                MERGE (t:Transaction {canonical_id: pod.canonical_id})
                CREATE (d:PODLine {
                    waybill_ref: pod.waybill_ref, 
                    part_id: pod.part_id, 
                    qty: toFloat(pod.qty_received_at_dock)
                })
                CREATE (d)-[:MAPS_TO]->(t)
            """, pods=prepared_pod)

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
                    "recoverable": round(variance, 2)
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
                    "recoverable": round(variance, 2)
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
                    "recoverable": round(record["total_billed"], 2)
                })

        report["total_recoverable_amount"] = round(report["total_recoverable_amount"], 2)
        return report
