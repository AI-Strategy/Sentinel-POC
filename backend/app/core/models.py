from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, index=True)
    vendor_name = Column(String)
    date = Column(String)
    sku = Column(String, index=True)
    description = Column(String)
    quantity = Column(Float)
    billed_unit_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(String, index=True)
    item_reference = Column(String, index=True)
    agreed_unit_price = Column(Float)
    status = Column(String)
    qty_authorized = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProofOfDelivery(Base):
    __tablename__ = "proof_of_delivery"

    id = Column(Integer, primary_key=True, index=True)
    waybill_ref = Column(String, index=True)
    part_id = Column(String, index=True)
    qty_received_at_dock = Column(Float)
    condition = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReconciliationReport(Base):
    __tablename__ = "reconciliation_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GhostFlagRecord(Base):
    __tablename__ = "ghost_flags"

    id = Column(Integer, primary_key=True, index=True)
    ghost_type = Column(String)
    severity = Column(String)
    invoice_id = Column(String, index=True)
    sku = Column(String, index=True)
    description = Column(String)
    financial_impact = Column(Float)
    narrative = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
