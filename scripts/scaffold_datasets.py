import os
import json
from pathlib import Path

def scaffold():
    base_dir = Path("data/sentenil_dirty_datasets")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = ["dataset_01", "dataset_02", "dataset_03", "dataset_04", "dataset_05_scale_10k"]
    
    for ds in datasets:
        ds_dir = base_dir / ds
        ds_dir.mkdir(exist_ok=True)
        
        # Create dummy data files
        invoice_template = [
            {
                "invoice_id": "INV-SCAF-01",
                "vendor_name": "SCAFFOLD VENDOR",
                "date": "2024-03-04",
                "line_items": [
                    {"sku": "SKU-CHILD-01", "description": "Child Component", "quantity": 10, "billed_unit_price": 5.0, "parent_sku": "SKU-PARENT-01"},
                    {"sku": "SKU-PARENT-01", "description": "Parent Assembly", "quantity": 1, "billed_unit_price": 100.0}
                ]
            }
        ]
        (ds_dir / "invoices.json").write_text(json.dumps(invoice_template, indent=2))
        (ds_dir / "purchase_orders.csv").write_text("PO_id,item_reference,agreed_unit_price,qty_authorized,status,currency\nPO-SCAF-01,SKU-PARENT-01,100.0,1,OPEN,USD\n")
        (ds_dir / "proof_of_delivery.xml").write_text('<Deliveries><delivery waybill_ref="WB-SCAF-01"><item part_id="SKU-PARENT-01" qty_received_at_dock="1" condition="GOOD"/></delivery></Deliveries>')
        
        # Create ground truth scaffold
        ground_truth = {
            "dataset": ds,
            "expected_flags": [
                {
                    "sku": "SCAFFOLD-SKU-01",
                    "type": "PRICE_VARIANCE",
                    "impact": 100.00,
                    "evidence": [
                        {"file": "invoices.json", "line": 10},
                        {"file": "purchase_orders.csv", "line": 2}
                    ]
                }
            ]
        }
        
        if ds == "dataset_05_scale_10k":
            ground_truth = {
                "dataset": ds,
                "summary_counts": {
                    "PRICE_VARIANCE": 50,
                    "QTY_MISMATCH": 30,
                    "PHANTOM_LINE": 20
                }
            }
            (ds_dir / "ground_truth_summary.json").write_text(json.dumps(ground_truth, indent=2))
        else:
            (ds_dir / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2))
            
        # Create empty report placeholder in output/reports
        report_dir = Path("output/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / f"{ds}.reconciliation_report.json").write_text(json.dumps({"flags": []}, indent=2))

    print(f"Scaffolded {len(datasets)} dataset directories and report placeholders.")

if __name__ == "__main__":
    scaffold()
