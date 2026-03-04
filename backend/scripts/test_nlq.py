"""
backend/scripts/test_nlq.py
--------------------------
Executes the NLQ Evaluation Matrix against the TextToCypherEngine.
"""

import json
import os
import sys
from pathlib import Path

# Add the app directory to the path so we can import from core
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

try:
    from app.core.nlq import TextToCypherEngine
    from app.core.llm import get_client
except ImportError as e:
    print(f"FAILED IMPORT: {e}")
    sys.exit(1)

def run_nlq_tests():
    # Load defaults from .env if needed
    uri      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user     = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "sentinel_neo4j")
    
    print(f"Connecting to Neo4j: {uri} (User: {user})")
    
    engine = TextToCypherEngine(uri, user, password)
    
    test_suite = [
        "What are the source file names and record indices for all HIGH severity phantom line flags?",
        "List the SKUs and the exact line hints in the source documents for all quantity mismatch flags.",
        "How many source document records are associated with price variance flags that have a financial impact greater than 100 dollars?",
        "For invoice INV-2024-0095, show the ghost type, the narrative, and the specific field names from the source documents used as evidence."
    ]

    results = []

    try:
        for i, question in enumerate(test_suite, 1):
            print(f"\n--- Executing Test {i} ---")
            print(f"NLQ: {question}")
            
            # Retrieve the Cypher query and execution results
            try:
                response = engine.execute_query(question)
                
                print(f"Generated Cypher:\n{response['cypher']}\n")
                if response['error']:
                    print(f"Execution Error: {response['error']}\n")
                else:
                    print(f"Records Returned: {len(response['results'])}\n")
                    
                results.append(response)
            except Exception as e:
                print(f"Engine Failure: {e}")

        # Output exact log for review
        output_path = backend_dir / "output" / "nlq_test_results.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"\nAudit complete. Results saved to: {output_path}")
            
    finally:
        engine.close()

if __name__ == "__main__":
    # Ensure client is available for Gemini queries
    client = get_client()
    if not client.available:
        print("FATAL: Gemini API Key not set. Test aborted.")
        sys.exit(1)
        
    run_nlq_tests()
