import sys
import os
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path("d:/Projects/Sentinel/repo/Sentinel-POC").absolute()))

from sentinel.main import _run_pipeline

invoice_path = "data/sentenil_dirty_datasets/dataset_01/invoices.json"
po_path      = "data/sentenil_dirty_datasets/dataset_01/purchase_orders.csv"
pod_path     = "data/sentenil_dirty_datasets/dataset_01/proof_of_delivery.xml"

try:
    report = _run_pipeline(
        invoice_path=invoice_path,
        po_path=po_path,
        pod_path=pod_path,
        use_llm=False,
        persist_neo4j=False
    )
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
