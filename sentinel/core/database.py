"""
sentinel/core/database.py
-------------------------
Handles interaction with the Postgres relational substrate.
Direct ingestion of raw records into the database.
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from .ingest import InvoiceLineItem, POLineItem, PODLineItem

logger = logging.getLogger(__name__)

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to individual vars if URL missing
        return psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "sentinel"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
    return psycopg2.connect(db_url)

def initialize_database():
    """Create the initial schema for the relational substrate."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Invoices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_invoice_lines (
                    id SERIAL PRIMARY KEY,
                    invoice_id TEXT,
                    vendor_name TEXT,
                    date DATE,
                    sku TEXT,
                    description TEXT,
                    quantity NUMERIC,
                    billed_unit_price NUMERIC,
                    source_ref JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # 2. POs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_po_lines (
                    id SERIAL PRIMARY KEY,
                    po_id TEXT,
                    item_reference TEXT,
                    agreed_unit_price NUMERIC,
                    status TEXT,
                    qty_authorized NUMERIC,
                    source_ref JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # 3. PODs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_pod_lines (
                    id SERIAL PRIMARY KEY,
                    waybill_ref TEXT,
                    part_id TEXT,
                    qty_received NUMERIC,
                    condition TEXT,
                    source_ref JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Relational substrate schema initialized.")
    finally:
        conn.close()

def save_invoices_to_db(items: list[InvoiceLineItem]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = [
                (
                    item.invoice_id, item.vendor_name, item.date, item.sku, 
                    item.description, item.quantity, item.billed_unit_price,
                    json.dumps({
                        "file": item.src_sku.file,
                        "record_index": item.src_sku.record_index,
                        "field": "line_item"
                    })
                ) for item in items
            ]
            execute_values(cur, """
                INSERT INTO raw_invoice_lines (
                    invoice_id, vendor_name, date, sku, description, quantity, billed_unit_price, source_ref
                ) VALUES %s
            """, data)
            conn.commit()
    finally:
        conn.close()

def save_pos_to_db(items: list[POLineItem]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = [
                (
                    item.po_id, item.item_reference, item.agreed_unit_price, 
                    item.status, item.qty_authorized,
                    json.dumps({
                        "file": item.src_row.file,
                        "record_index": item.src_row.record_index,
                        "line_hint": item.src_row.line_hint
                    })
                ) for item in items
            ]
            execute_values(cur, """
                INSERT INTO raw_po_lines (
                    po_id, item_reference, agreed_unit_price, status, qty_authorized, source_ref
                ) VALUES %s
            """, data)
            conn.commit()
    finally:
        conn.close()

def save_pods_to_db(items: list[PODLineItem]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = [
                (
                    item.waybill_ref, item.part_id, item.qty_received_at_dock, 
                    item.condition,
                    json.dumps({
                        "file": item.src_element.file if item.src_element else "database",
                        "record_index": item.src_element.record_index if item.src_element else 0
                    })
                ) for item in items
            ]
            execute_values(cur, """
                INSERT INTO raw_pod_lines (
                    waybill_ref, part_id, qty_received, condition, source_ref
                ) VALUES %s
            """, data)
            conn.commit()
    finally:
        conn.close()

# ── Retrieval ──────────────────────────────────────────────────────────────────

def fetch_invoices_from_db() -> list[InvoiceLineItem]:
    from .ingest import SourceRef
    conn = get_db_connection()
    items = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT invoice_id, vendor_name, date, sku, description, quantity, billed_unit_price, id, source_ref FROM raw_invoice_lines")
            for row in cur.fetchall():
                src = row[8] if row[8] else {}
                ref = SourceRef(file=src.get("file", "postgres"), record_index=row[7], line_hint=None, field="db_record")
                items.append(InvoiceLineItem(
                    invoice_id=row[0], vendor_name=row[1], date=str(row[2]),
                    sku=row[3], description=row[4], quantity=float(row[5]),
                    billed_unit_price=float(row[6]),
                    src_invoice_id=ref, src_sku=ref, src_quantity=ref, src_billed_unit_price=ref
                ) )
    finally:
        conn.close()
    return items

def fetch_pos_from_db() -> list[POLineItem]:
    from .ingest import SourceRef
    conn = get_db_connection()
    items = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT po_id, item_reference, agreed_unit_price, status, qty_authorized, id, source_ref FROM raw_po_lines")
            for row in cur.fetchall():
                src = row[6] if row[6] else {}
                ref = SourceRef(file=src.get("file", "postgres"), record_index=row[5], line_hint=src.get("line_hint"), field="db_record")
                items.append(POLineItem(
                    po_id=row[0], item_reference=row[1], agreed_unit_price=float(row[2]),
                    status=row[3], qty_authorized=float(row[4]),
                    src_row=ref, src_agreed_unit_price=ref, src_qty_authorized=ref
                ))
    finally:
        conn.close()
    return items

def fetch_pods_from_db() -> list[PODLineItem]:
    from .ingest import SourceRef
    conn = get_db_connection()
    items = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT waybill_ref, part_id, qty_received, condition, id, source_ref FROM raw_pod_lines")
            for row in cur.fetchall():
                src = row[5] if row[5] else {}
                ref = SourceRef(file=src.get("file", "postgres"), record_index=row[4], line_hint=None, field="db_record")
                items.append(PODLineItem(
                    waybill_ref=row[0], part_id=row[1], qty_received_at_dock=float(row[2]),
                    condition=row[3], src_element=ref, src_qty_received=ref
                ))
    finally:
        conn.close()
    return items
