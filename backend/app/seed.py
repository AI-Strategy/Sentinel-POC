import os
from .core.db import SessionLocal, engine, Base
from .core.models import Invoice, PurchaseOrder, ProofOfDelivery
from .core.ingest import Ingestor

def seed_database():
    print("--- Initializing Postgres Schema (Phase 0 Baseline) ---")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Path inside Docker is /app /data
    data_dir = "data"
    if not os.path.exists(data_dir):
        data_dir = "../../data"

    print(f"--- Ingesting sample data from {data_dir} ---")
    
    try:
        # Load Invoices (Phase 1 flat structure)
        invoices = Ingestor.ingest_invoice(os.path.join(data_dir, "invoices.json"))
        for inv in invoices:
            db.add(Invoice(
                invoice_id=inv.get("invoice_id"),
                vendor_name=inv.get("vendor_name"),
                date=inv.get("date"),
                sku=inv.get("sku"),
                description=inv.get("description"),
                quantity=float(inv.get("quantity", 0)),
                billed_unit_price=float(inv.get("billed_unit_price", 0))
            ))
            
        # Load POs
        pos = Ingestor.ingest_po(os.path.join(data_dir, "purchase_orders.csv"))
        for po in pos:
            db.add(PurchaseOrder(
                po_id=po.get("PO_id"),
                item_reference=po.get("item_reference"),
                agreed_unit_price=float(po.get("agreed_unit_price", 0)),
                status=po.get("status"),
                qty_authorized=float(po.get("qty_authorized", 0))
            ))
            
        # Load PODs
        pods = Ingestor.ingest_pod(os.path.join(data_dir, "proof_of_delivery.xml"))
        for pod in pods:
            db.add(ProofOfDelivery(
                waybill_ref=pod.get("waybill_ref"),
                part_id=pod.get("part_id"),
                qty_received_at_dock=float(pod.get("qty_received_at_dock", 0)),
                condition=pod.get("condition")
            ))
            
        db.commit()
        print("[SUCCESS] Postgres Substrate seeded with flat Phase 1 data.")
        
    except Exception as e:
        db.rollback()
        print(f"[FAILED] Seeding error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
