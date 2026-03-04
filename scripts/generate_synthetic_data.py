"""
scripts/generate_synthetic_data.py
----------------------------------
Generates 25 synthetic transactions (mix of clean and dirty) 
and populates the Postgres relational substrate.
"""

import os
import json
import random
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "sentinel"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
    return psycopg2.connect(db_url)

def clear_tables(cur):
    cur.execute("TRUNCATE raw_invoice_lines, raw_po_lines, raw_pod_lines RESTART IDENTITY;")

def generate_data():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            clear_tables(cur)
            
            skus = [f"SKU-{i:03d}" for i in range(1, 30)]
            vendors = ["Titan Logistics", "Apex Industrial", "Global Parts Corp"]
            
            # We want 25 Invoice Lines
            for i in range(1, 26):
                invoice_id = f"INV-SYN-{1000 + i}"
                po_id = f"PO-SYN-{2000 + i}"
                waybill = f"WB-SYN-{3000 + i}"
                sku = random.choice(skus)
                vendor = random.choice(vendors)
                date = (datetime.now() - timedelta(days=random.randint(1, 30))).date()
                
                base_price = round(random.uniform(50, 500), 2)
                base_qty = float(random.randint(10, 100))
                
                scenario = random.choices(
                    ["CLEAN", "PRICE_VAR", "QTY_MIS", "PHANTOM", "DIRTY"], 
                    weights=[10, 5, 5, 3, 2]
                )[0]
                
                inv_price = base_price
                inv_qty = base_qty
                po_price = base_price
                po_qty_auth = base_qty
                pod_qty = base_qty
                
                is_dirty = False
                
                if scenario == "PRICE_VAR":
                    inv_price = base_price + 25.0
                elif scenario == "QTY_MIS":
                    pod_qty = base_qty - 5.0
                elif scenario == "PHANTOM":
                    sku = f"GHOST-{random.randint(100, 999)}"
                    # No PO or POD for this one
                elif scenario == "DIRTY":
                    is_dirty = True
                    # We'll store it as a string with a comma in the DB if we want to test parsing, 
                    # but the DB column is NUMERIC. The generator should simulate the LOADED state.
                    # Or we skip the "raw string" part for now since DB is typed.
                    sku = sku.lower().replace("-", " ") # Fuzzy SKU
                
                # 1. Save PO
                if scenario != "PHANTOM":
                    cur.execute("""
                        INSERT INTO raw_po_lines (po_id, item_reference, agreed_unit_price, status, qty_authorized, source_ref)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (po_id, sku if not is_dirty else sku.upper().replace(" ", "-"), po_price, "OPEN", po_qty_auth, json.dumps({"origin": "synthetic_po"})))
                
                # 2. Save POD
                if scenario != "PHANTOM":
                    cur.execute("""
                        INSERT INTO raw_pod_lines (waybill_ref, part_id, qty_received, condition, source_ref)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (waybill, sku if not is_dirty else sku.upper().replace(" ", "-"), pod_qty, "GOOD", json.dumps({"origin": "synthetic_pod"})))
                
                # 3. Save Invoice
                cur.execute("""
                    INSERT INTO raw_invoice_lines (invoice_id, vendor_name, date, sku, description, quantity, billed_unit_price, source_ref)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (invoice_id, vendor, date, sku, f"Synthetic item {sku}", inv_qty, inv_price, json.dumps({"origin": "synthetic_inv"})))

            conn.commit()
            print("✅ Successfully generated 25 synthetic transactions in Postgres.")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_data()
