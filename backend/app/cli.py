#!/usr/bin/env python3
import argparse
import sys
import logging
from pathlib import Path
from .core.ingest import load_invoices, load_purchase_orders, load_pod
from .core.match import link_transactions
from .core.detect import detect_ghosts
from .core.report import write_reports
from .core.graph import persist_to_neo4j, run_gds_anomaly_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("sentinel.cli")

def main():
    p = argparse.ArgumentParser(description="Sentinel Ghost Invoice Reconciliation")
    p.add_argument("--invoice",    default="data/invoices.json")
    p.add_argument("--po",         default="data/purchase_orders.csv")
    p.add_argument("--pod",        default="data/proof_of_delivery.xml")
    p.add_argument("--output",     default="output/")
    p.add_argument("--no-llm",     action="store_true")
    p.add_argument("--neo4j",      action="store_true")
    p.add_argument("--neo4j-uri",  default="bolt://localhost:7687")
    p.add_argument("--neo4j-user", default="neo4j")
    p.add_argument("--neo4j-pass", default="password")
    p.add_argument("--gds",        action="store_true")
    args = p.parse_args()

    logger.info("Step 1/5 — Ingesting source files …")
    invoices = load_invoices(args.invoice)
    pos = load_purchase_orders(args.po)
    pods = load_pod(args.pod)

    logger.info("Step 2/5 — Linking transactions …")
    transactions = link_transactions(invoices, pos, pods, use_llm=not args.no_llm)

    logger.info("Step 3/5 — Running Ghost leakage detection …")
    flags = detect_ghosts(transactions)

    logger.info("Step 4/5 — Writing evidence reports …")
    write_reports(flags, transactions, output_dir=args.output)

    if args.neo4j:
        logger.info("Step 5/5 — Persisting graph to Neo4j …")
        persist_to_neo4j(transactions, flags, uri=args.neo4j_uri, user=args.neo4j_user, password=args.neo4j_pass)
        if args.gds:
            run_gds_anomaly_analysis(uri=args.neo4j_uri, user=args.neo4j_user, password=args.neo4j_pass)

    logger.info("✅ Sentinel run complete.")

if __name__ == "__main__":
    main()
