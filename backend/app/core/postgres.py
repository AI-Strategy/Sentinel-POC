"""
backend/app/core/postgres.py
--------------------------
Postgres persistence layer.

Stores TWO categories of data:

  1. RAW DOCUMENTS — the verbatim ingested content before any LLM processing.
     Table: sentinel.raw_documents

  2. EXTRACTED ENTITIES — the structured JSON output from entity_extractor.py.
     Tables (normalised):
       sentinel.extractions       — one row per extraction run
       sentinel.entities_vendor
       sentinel.entities_item
       sentinel.entities_invoice
       sentinel.entities_invoice_line
       sentinel.entities_purchase_order
       sentinel.entities_delivery
       sentinel.relations
       sentinel.anomalies

Schema is created automatically on first connect (idempotent DDL).

Connection:
  - Via DATABASE_URL env var  OR  explicit dsn= parameter
  - Uses psycopg2 (sync); connection pooling via SimpleConnectionPool
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

logger = logging.getLogger(__name__)

# ── DDL ───────────────────────────────────────────────────────────────────────

_DDL = """
CREATE SCHEMA IF NOT EXISTS sentinel;

-- ── Raw documents ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.raw_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file     TEXT NOT NULL,
    file_type       TEXT,                       -- json | csv | xml | xlsx | pdf | png …
    document_type   TEXT,                       -- invoice | purchase_order | delivery | unknown
    connector_type  TEXT,                       -- sql | rest | sap | salesforce | upload | null
    raw_content     JSONB,                      -- full parsed records array
    raw_text        TEXT,                       -- verbatim text (for PDF / image OCR)
    byte_size       BIGINT,
    page_count      INT,
    used_vision     BOOLEAN DEFAULT FALSE,
    parse_errors    JSONB
);

CREATE INDEX IF NOT EXISTS idx_raw_doc_source   ON sentinel.raw_documents (source_file);
CREATE INDEX IF NOT EXISTS idx_raw_doc_type     ON sentinel.raw_documents (document_type);
CREATE INDEX IF NOT EXISTS idx_raw_doc_ingested ON sentinel.raw_documents (ingested_at DESC);

-- ── Extraction runs ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.extractions (
    extraction_id   UUID PRIMARY KEY,
    raw_document_id UUID REFERENCES sentinel.raw_documents(id) ON DELETE SET NULL,
    extracted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_file     TEXT,
    document_type   TEXT,
    used_vision     BOOLEAN DEFAULT FALSE,
    llm_model       TEXT,
    entity_counts   JSONB,                      -- {"vendors":1, "items":3, ...}
    anomaly_count   INT DEFAULT 0,
    relation_count  INT DEFAULT 0,
    extraction_error TEXT
);

-- ── Vendors ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.entities_vendor (
    vendor_id       TEXT NOT NULL,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    name            TEXT,
    name_variants   JSONB,
    confidence      FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (vendor_id, extraction_id)
);

-- ── Items / SKUs ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.entities_item (
    item_id         TEXT NOT NULL,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    sku             TEXT,
    description     TEXT,
    unit            TEXT,
    category        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (item_id, extraction_id)
);

-- ── Invoices ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.entities_invoice (
    invoice_id      TEXT NOT NULL,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    vendor_id       TEXT,
    date            DATE,
    currency        TEXT DEFAULT 'USD',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (invoice_id, extraction_id)
);

CREATE TABLE IF NOT EXISTS sentinel.entities_invoice_line (
    id              BIGSERIAL PRIMARY KEY,
    invoice_id      TEXT,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    item_id         TEXT,
    sku             TEXT,
    qty             NUMERIC,
    unit_price      NUMERIC(18,4),
    total           NUMERIC(18,4),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Purchase Orders ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.entities_purchase_order (
    po_id           TEXT NOT NULL,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    item_id         TEXT,
    agreed_price    NUMERIC(18,4),
    qty_authorized  NUMERIC,
    status          TEXT,
    currency        TEXT DEFAULT 'USD',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (po_id, item_id, extraction_id)
);

-- ── Deliveries ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.entities_delivery (
    waybill_ref     TEXT NOT NULL,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    item_id         TEXT,
    qty_received    NUMERIC,
    condition       TEXT,
    delivery_date   DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (waybill_ref, item_id, extraction_id)
);

-- ── Relations ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.relations (
    id              BIGSERIAL PRIMARY KEY,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    from_type       TEXT,
    from_id         TEXT,
    relation        TEXT,
    to_type         TEXT,
    to_id           TEXT,
    properties      JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relations_extraction ON sentinel.relations (extraction_id);
CREATE INDEX IF NOT EXISTS idx_relations_from       ON sentinel.relations (from_type, from_id);

-- ── Anomalies ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel.anomalies (
    id              BIGSERIAL PRIMARY KEY,
    extraction_id   UUID REFERENCES sentinel.extractions(extraction_id) ON DELETE CASCADE,
    anomaly_type    TEXT,
    description     TEXT,
    severity        TEXT,
    entity_refs     JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomalies_type     ON sentinel.anomalies (anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON sentinel.anomalies (severity);
"""


# ── Connection pool ───────────────────────────────────────────────────────────

class PostgresStore:
    """
    Postgres persistence for Sentinel raw docs and extracted entities.

    Usage:
        store = PostgresStore()          # reads DATABASE_URL from env
        store = PostgresStore(dsn="postgresql://user:pw@localhost/sentinel")
    """

    def __init__(
        self,
        dsn: str | None = None,
        min_conn: int = 1,
        max_conn: int = 10,
    ):
        self.dsn = dsn or os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/sentinel"
        )
        self._pool = None
        self._connect(min_conn, max_conn)

    def _connect(self, min_conn: int, max_conn: int):
        try:
            import psycopg2
            from psycopg2 import pool as pg_pool
            self._pool = pg_pool.SimpleConnectionPool(
                min_conn, max_conn, self.dsn
            )
            self._apply_schema()
            logger.info("Postgres connected: %s", self.dsn.split("@")[-1])
        except ImportError:
            raise RuntimeError("psycopg2 not installed. Run: pip install psycopg2-binary")
        except Exception as exc:
            logger.error("Postgres connection failed: %s", exc)
            raise

    @contextmanager
    def _conn(self) -> Generator:
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def _apply_schema(self):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(_DDL)
        logger.info("Postgres schema applied (sentinel.*)")

    def close(self):
        if self._pool:
            self._pool.closeall()

    # ── Raw document storage ──────────────────────────────────────────────────

    def store_raw_document(
        self,
        source_file: str,
        file_type: str,
        document_type: str,
        raw_content: list[dict] | None = None,
        raw_text: str = "",
        connector_type: str | None = None,
        byte_size: int = 0,
        page_count: int = 0,
        used_vision: bool = False,
        parse_errors: list[str] | None = None,
    ) -> str:
        """Insert a raw document row. Returns the new UUID."""
        doc_id = str(uuid.uuid4())
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sentinel.raw_documents
                        (id, source_file, file_type, document_type, connector_type,
                         raw_content, raw_text, byte_size, page_count, used_vision, parse_errors)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        doc_id,
                        source_file,
                        file_type,
                        document_type,
                        connector_type,
                        json.dumps(raw_content or []),
                        raw_text or "",
                        byte_size,
                        page_count,
                        used_vision,
                        json.dumps(parse_errors or []),
                    ),
                )
        logger.debug("Stored raw_document %s (%s)", doc_id, source_file)
        return doc_id

    # ── Extracted entity storage ──────────────────────────────────────────────

    def store_extraction(
        self,
        extraction: dict,
        raw_document_id: str | None = None,
        llm_model: str = "gemini-2.0-flash",
    ) -> str:
        """
        Persist a full extraction envelope (from entity_extractor.py).
        Returns extraction_id.
        """
        eid    = extraction["extraction_id"]
        ents   = extraction.get("entities", {})
        rels   = extraction.get("relations", [])
        anoms  = extraction.get("anomalies", [])

        entity_counts = {k: len(v) for k, v in ents.items()}

        with self._conn() as conn:
            with conn.cursor() as cur:
                # ── extractions header ─────────────────────────────────────
                cur.execute(
                    """
                    INSERT INTO sentinel.extractions
                        (extraction_id, raw_document_id, extracted_at, source_file,
                         document_type, used_vision, llm_model,
                         entity_counts, anomaly_count, relation_count, extraction_error)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (extraction_id) DO NOTHING
                    """,
                    (
                        eid,
                        raw_document_id,
                        extraction.get("extracted_at"),
                        extraction.get("source_file"),
                        extraction.get("document_type"),
                        extraction.get("used_vision", False),
                        llm_model,
                        json.dumps(entity_counts),
                        len(anoms),
                        len(rels),
                        extraction.get("error"),
                    ),
                )

                # ── vendors ───────────────────────────────────────────────
                for v in ents.get("vendors", []):
                    cur.execute(
                        """
                        INSERT INTO sentinel.entities_vendor
                            (vendor_id, extraction_id, name, name_variants, confidence)
                        VALUES (%s,%s,%s,%s,%s)
                        ON CONFLICT (vendor_id, extraction_id) DO UPDATE
                        SET name=EXCLUDED.name, name_variants=EXCLUDED.name_variants
                        """,
                        (v.get("vendor_id"), eid, v.get("name"),
                         json.dumps(v.get("name_variants", [])), v.get("confidence")),
                    )

                # ── items ─────────────────────────────────────────────────
                for item in ents.get("items", []):
                    cur.execute(
                        """
                        INSERT INTO sentinel.entities_item
                            (item_id, extraction_id, sku, description, unit, category)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (item_id, extraction_id) DO UPDATE
                        SET description=EXCLUDED.description
                        """,
                        (item.get("item_id"), eid, item.get("sku"),
                         item.get("description"), item.get("unit"), item.get("category")),
                    )

                # ── invoices + line items ─────────────────────────────────
                for inv in ents.get("invoices", []):
                    cur.execute(
                        """
                        INSERT INTO sentinel.entities_invoice
                            (invoice_id, extraction_id, vendor_id, date, currency)
                        VALUES (%s,%s,%s,%s,%s)
                        ON CONFLICT (invoice_id, extraction_id) DO NOTHING
                        """,
                        (inv.get("invoice_id"), eid, inv.get("vendor_id"),
                         inv.get("date") or None, inv.get("currency", "USD")),
                    )
                    for li in inv.get("line_items", []):
                        cur.execute(
                            """
                            INSERT INTO sentinel.entities_invoice_line
                                (invoice_id, extraction_id, item_id, sku, qty, unit_price, total)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            """,
                            (inv.get("invoice_id"), eid, li.get("item_id"),
                             li.get("sku"), li.get("qty"), li.get("unit_price"), li.get("total")),
                        )

                # ── purchase orders ───────────────────────────────────────
                for po in ents.get("purchase_orders", []):
                    cur.execute(
                        """
                        INSERT INTO sentinel.entities_purchase_order
                            (po_id, extraction_id, item_id, agreed_price,
                             qty_authorized, status, currency)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (po_id, item_id, extraction_id) DO NOTHING
                        """,
                        (po.get("po_id"), eid, po.get("item_id"),
                         po.get("agreed_price"), po.get("qty_authorized"),
                         po.get("status"), po.get("currency", "USD")),
                    )

                # ── deliveries ────────────────────────────────────────────
                for d in ents.get("deliveries", []):
                    cur.execute(
                        """
                        INSERT INTO sentinel.entities_delivery
                            (waybill_ref, extraction_id, item_id, qty_received,
                             condition, delivery_date)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (waybill_ref, item_id, extraction_id) DO NOTHING
                        """,
                        (d.get("waybill_ref"), eid, d.get("item_id"),
                         d.get("qty_received"), d.get("condition"),
                         d.get("delivery_date") or None),
                    )

                # ── relations ─────────────────────────────────────────────
                for rel in rels:
                    cur.execute(
                        """
                        INSERT INTO sentinel.relations
                            (extraction_id, from_type, from_id,
                             relation, to_type, to_id, properties)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (eid, rel.get("from_type"), rel.get("from_id"),
                         rel.get("relation"), rel.get("to_type"), rel.get("to_id"),
                         json.dumps(rel.get("properties", {}))),
                    )

                # ── anomalies ─────────────────────────────────────────────
                for anom in anoms:
                    cur.execute(
                        """
                        INSERT INTO sentinel.anomalies
                            (extraction_id, anomaly_type, description,
                             severity, entity_refs)
                        VALUES (%s,%s,%s,%s,%s)
                        """,
                        (eid, anom.get("type"), anom.get("description"),
                         anom.get("severity"), json.dumps(anom.get("entity_refs", []))),
                    )

        logger.info(
            "Stored extraction %s: %s entities, %d relations, %d anomalies",
            eid, entity_counts, len(rels), len(anoms),
        )
        return eid

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_recent_extractions(self, limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT extraction_id, extracted_at, source_file,
                           document_type, entity_counts, anomaly_count,
                           relation_count, extraction_error
                    FROM sentinel.extractions
                    ORDER BY extracted_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_anomalies(
        self,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                if severity:
                    cur.execute(
                        "SELECT * FROM sentinel.anomalies WHERE severity=%s ORDER BY created_at DESC LIMIT %s",
                        (severity, limit),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM sentinel.anomalies ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_raw_documents(self, limit: int = 50) -> list[dict]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, ingested_at, source_file, file_type,
                           document_type, connector_type, byte_size,
                           page_count, used_vision
                    FROM sentinel.raw_documents
                    ORDER BY ingested_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
