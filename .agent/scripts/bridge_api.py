import subprocess
import os
import sys
import json

def generate_bridge(backend_type="python"):
    print(f"🌉 Building API Bridge for {backend_type}...")
    
    # 1. Extract Schema
    if backend_type == "python":
        # Assumes FastAPI exports JSON
        subprocess.run("python scripts/extract_openapi.py > openapi.json", shell=True, check=True)
    elif backend_type == "rust":
        # Assumes Axum binary exports JSON
        subprocess.run("cargo run --bin gen-spec > openapi.json", shell=True, check=True)
        
    # 2. Generate Client (React/Query)
    # Using 'openapi-typescript' for strict types
    print("🔨 Generating TypeScript Client...")
    cmd = "npx openapi-typescript openapi.json -o ./frontend/src/lib/api-schema.d.ts"
    subprocess.run(cmd, shell=True, check=True)
    
    print("✅ Bridge Built. Frontend types are now synced 1:1 with Backend.")

if __name__ == "__main__":
    backend = sys.argv[1] if len(sys.argv) > 1 else "python"
    generate_bridge(backend)
