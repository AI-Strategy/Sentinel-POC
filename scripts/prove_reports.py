import json
import asyncio
import httpx
import os
from pathlib import Path

# API configuration
API_URL = "https://localhost:8000"
USER = "admin"
PASS = "sentinel2026"

async def prove_reports():
    # verify=False because we are using self-signed certs locally
    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        print("--- Reporting Proof of Concept (POC) Verification ---")
        
        # 1. Login to get JWT Token
        print("\n[Action] Authenticating as 'admin'...")
        try:
            login_resp = await client.post(f"{API_URL}/api/auth/login", json={
                "username": USER,
                "password": PASS
            })
            login_resp.raise_for_status()
            token = login_resp.json()["access_token"]
            print(f"OK: Logged in successfully. Token: {token[:20]}...")
            # Set auth header for following calls
            client.headers.update({"Authorization": f"Bearer {token}"})
        except Exception as e:
            print(f"FAILED: Login failed: {e}")
            return

        # 2. Trigger fresh reconciliation
        print("\n[Action] Triggering Reconciliation via JWT-Authenticated API...")
        try:
            resp = await client.post(f"{API_URL}/reconcile", json={
                "invoice_path": "data/sentenil_dirty_datasets/dataset_01/invoices.json",
                "po_path": "data/sentenil_dirty_datasets/dataset_01/purchase_orders.csv",
                "pod_path": "data/sentenil_dirty_datasets/dataset_01/proof_of_delivery.xml",
                "use_llm": False,
                "persist_neo4j": False
            })
            resp.raise_for_status()
            print("OK: Reconciliation Complete (HTTP 200)")
        except Exception as e:
            print(f"FAILED: Reconcile error: {e}")
            return

        # 3. PROVE JSON Report
        print("\n[Proof 1/3] Downloading Structured JSON...")
        resp = await client.get(f"{API_URL}/report/latest")
        if resp.status_code == 200:
            data = resp.json()
            print(f"OK: JSON Found. Total Exposure: ${data['report_meta'].get('total_financial_exposure_usd', 0):,.2f}")
        else:
            print(f"FAILED: JSON download (HTTP {resp.status_code})")

        # 4. PROVE Markdown Report
        print("\n[Proof 2/3] Downloading Forensic Markdown...")
        resp = await client.get(f"{API_URL}/report/latest/markdown")
        if resp.status_code == 200:
            text = resp.text
            print(f"OK: Markdown Found ({len(text)} bytes)")
        else:
            print(f"FAILED: Markdown download (HTTP {resp.status_code})")

        # 5. PROVE PDF Download
        print("\n[Proof 3/3] Downloading Claim-Level PDF Evidence Package...")
        resp = await client.get(f"{API_URL}/report/latest/pdf")
        if resp.status_code == 200:
            content = resp.content
            print(f"OK: PDF Received ({len(content)} bytes)")
            if content.startswith(b"%PDF-1."):
                print(f"   Signature check passed: Valid PDF header found.")
            
            # Save local proof copy
            proof_path = Path("output/sentinel_report_proof.pdf")
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            proof_path.write_bytes(content)
            print(f"   Proof file saved locally: {proof_path}")
        else:
            print(f"FAILED: PDF download (HTTP {resp.status_code})")

if __name__ == "__main__":
    asyncio.run(prove_reports())
