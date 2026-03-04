"""
scripts/benchmark_sentinel.py
----------------------------
Performance & Verification Suite for Phase 1.
Generates 10k rows of dirty data and benchmarks the reconciliation engine.
"""

import json
import csv
import time
import os
import random
import psutil
from pathlib import Path
import sys

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sentinel.core.ingest import InvoiceLineItem, POLineItem, PODLineItem, SourceRef, load_invoices, load_purchase_orders, load_pod
from sentinel.core.match import link_transactions
from sentinel.core.detect import detect_ghosts
from sentinel.core.report import build_json_report

BENCH_DIR = Path("data/benchmark")

def generate_dirty_data(count=10000):
    BENCH_DIR.mkdir(parents=True, exist_ok=True)
    
    invoices = []
    pos = []
    pods = []
    
    total_leakage = 0.0
    
    for i in range(count):
        sku = f"SKU-{i:05d}"
        qty = random.randint(10, 100)
        price = round(random.uniform(5.0, 500.0), 2)
        
        # Decide scenario
        scenario = random.choices(
            ["MATCH", "PRICE_VAR", "QTY_VAR", "PHANTOM"],
            weights=[70, 10, 10, 10]
        )[0]
        
        if scenario == "MATCH":
            # Clean transaction
            pos.append({
                "PO_id": f"PO-{i}", "item_reference": sku, "agreed_unit_price": price,
                "status": "APPROVED", "qty_authorized": qty
            })
            pods.append({
                "waybill_ref": f"WB-{i}", "part_id": sku, "qty_received_at_dock": qty, "condition": "GOOD"
            })
            invoices.append({
                "invoice_id": f"INV-{i}", "vendor_name": "BENCH-VENDOR", "date": "2026-03-04",
                "line_items": [{"sku": sku, "description": f"Item {i}", "quantity": qty, "billed_unit_price": price}]
            })
            
        elif scenario == "PRICE_VAR":
            # PO has lower price than Invoice
            po_price = round(price * 0.8, 2)
            leakage = round((price - po_price) * qty, 2)
            total_leakage += leakage
            
            pos.append({
                "PO_id": f"PO-{i}", "item_reference": sku, "agreed_unit_price": po_price,
                "status": "APPROVED", "qty_authorized": qty
            })
            pods.append({
                "waybill_ref": f"WB-{i}", "part_id": sku, "qty_received_at_dock": qty, "condition": "GOOD"
            })
            invoices.append({
                "invoice_id": f"INV-{i}", "vendor_name": "BENCH-VENDOR", "date": "2026-03-04",
                "line_items": [{"sku": sku, "description": f"Item {i}", "quantity": qty, "billed_unit_price": price}]
            })
            
        elif scenario == "QTY_VAR":
            # Received less than invoiced
            rec_qty = qty - 2
            leakage = round(2 * price, 2)
            total_leakage += leakage
            
            pos.append({
                "PO_id": f"PO-{i}", "item_reference": sku, "agreed_unit_price": price,
                "status": "APPROVED", "qty_authorized": qty
            })
            pods.append({
                "waybill_ref": f"WB-{i}", "part_id": sku, "qty_received_at_dock": rec_qty, "condition": "DAMAGED"
            })
            invoices.append({
                "invoice_id": f"INV-{i}", "vendor_name": "BENCH-VENDOR", "date": "2026-03-04",
                "line_items": [{"sku": sku, "description": f"Item {i}", "quantity": qty, "billed_unit_price": price}]
            })
            
        elif scenario == "PHANTOM":
            # Invoiced but no PO
            leakage = round(qty * price, 2)
            total_leakage += leakage
            
            # No PO, maybe a POD exists but it's unauthorized
            pods.append({
                "waybill_ref": f"WB-{i}", "part_id": sku, "qty_received_at_dock": qty, "condition": "GOOD"
            })
            invoices.append({
                "invoice_id": f"INV-{i}", "vendor_name": "BENCH-VENDOR", "date": "2026-03-04",
                "line_items": [{"sku": sku, "description": f"Item {i}", "quantity": qty, "billed_unit_price": price}]
            })

    # Save files
    with open(BENCH_DIR / "invoices.json", "w") as f:
        json.dump(invoices, f)
    
    with open(BENCH_DIR / "purchase_orders.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=pos[0].keys())
        writer.writeheader()
        writer.writerows(pos)
        
    with open(BENCH_DIR / "proof_of_delivery.xml", "w") as f:
        f.write("<deliveries>\n")
        for p in pods:
            f.write(f'  <delivery waybill_ref="{p["waybill_ref"]}">\n')
            f.write(f'    <item part_id="{p["part_id"]}" qty_received_at_dock="{p["qty_received_at_dock"]}" condition="{p["condition"]}" />\n')
            f.write("  </delivery>\n")
        f.write("</deliveries>")
        
    return total_leakage

def run_benchmark():
    print("Sentinel Phase 1 Benchmark - 10k Row Stress Test")
    print("-" * 50)
    
    # 1. Generate data
    print("Generating 10,000 records of dirty data...")
    expected_leakage = generate_dirty_data(10000)
    print(f"Dataset generated. Expected leakage: ${expected_leakage:,.2f}")
    
    # 2. Bench Ingestion
    print("\nPhase A: Ingestion & Normalization")
    start = time.perf_counter()
    invoices = load_invoices(BENCH_DIR / "invoices.json")
    pos = load_purchase_orders(BENCH_DIR / "purchase_orders.csv")
    pods = load_pod(BENCH_DIR / "proof_of_delivery.xml")
    end = time.perf_counter()
    print(f"DONE: Ingested {len(invoices)} invoice lines in {end-start:.3f}s")
    
    # 3. Bench Matching
    print("\nPhase B: Mapping Logic (Exact + RapidFuzz)")
    start = time.perf_counter()
    # Disable LLM for benchmark to measure pure engine speed
    transactions = link_transactions(invoices, pos, pods, use_llm=False)
    end = time.perf_counter()
    print(f"DONE: Linked {len(transactions)} transactions in {end-start:.3f}s")
    
    # 4. Bench Detection
    print("\nPhase C: Leakage Detection Logic")
    start = time.perf_counter()
    flags = detect_ghosts(transactions)
    end = time.perf_counter()
    print(f"DONE: Flagged {len(flags)} anomalies in {end-start:.3f}s")
    
    # 5. Bench Reporting
    print("\nPhase D: Evidence Chain Generator")
    start = time.perf_counter()
    report = build_json_report(flags, transactions)
    end = time.perf_counter()
    print(f"DONE: Generated Evidence Package in {end-start:.3f}s")
    
    # 6. Final Audit
    total_time = (end - start) # this is just report time, let's recalculate total
    # re-start from full run
    
    print("\n" + "="*50)
    print("FULL PIPELINE AUDIT")
    print("="*50)
    
    start_all = time.perf_counter()
    invoices = load_invoices(BENCH_DIR / "invoices.json")
    pos = load_purchase_orders(BENCH_DIR / "purchase_orders.csv")
    pods = load_pod(BENCH_DIR / "proof_of_delivery.xml")
    txns = link_transactions(invoices, pos, pods, use_llm=False)
    ghosts = detect_ghosts(txns)
    rep = build_json_report(ghosts, txns)
    end_all = time.perf_counter()
    
    actual_leakage = rep["report_meta"]["total_recoverable_amount_usd"]
    process = psutil.Process(os.getpid())
    mem_usage = process.memory_info().rss / (1024 * 1024)
    
    print(f"Total Rows:     10,000")
    print(f"Total Time:     {end_all - start_all:.3f} seconds")
    print(f"Throughput:    {10000 / (end_all - start_all):.1f} rows/sec")
    print(f"Memory Usage:  {mem_usage:.1f} MB")
    print(f"Detected Leak: ${actual_leakage:,.2f}")
    print(f"Expted Leak:   ${expected_leakage:,.2f}")
    
    if abs(actual_leakage - expected_leakage) < 1.0:
        print("\nVERDICT: COMPLIANT (High Precision)")
    else:
        print(f"\nWARNING: DISCREPANCY of ${abs(actual_leakage - expected_leakage):.2f}")
        
    if (end_all - start_all) < 10.0:
        print("VERDICT: PERFORMANCE PASS (< 10s)")
    else:
        print("❌ VERDICT: PERFORMANCE FAIL (> 10s)")

if __name__ == "__main__":
    run_benchmark()
