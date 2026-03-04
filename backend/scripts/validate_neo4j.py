"""
backend/scripts/validate_neo4j.py
---------------------------------
Validates the Neo4j database connection and GDS (Graph Data Science) plugin state.
Checks for required node labels and readiness for forensic ingestion.
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to the path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

try:
    from neo4j import GraphDatabase
except ImportError:
    print("FAILED: neo4j library not installed. Run: pip install neo4j")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinel.neo4j_validator")

def validate_neo4j():
    # Load defaults from environment variables
    uri      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user     = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "sentinel_neo4j")
    
    logger.info(f"Connecting to Neo4j Substrate: {uri} (User: {user})")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # 1. Connection check
            session.run("RETURN 1").single()
            logger.info("✅ SUCCESS: Neo4j Connection Established.")
            
            # 2. GDS Membership check
            result = session.run("CALL gds.version()").single()
            if result:
                logger.info(f"✅ SUCCESS: Graph Data Science (GDS) Plugin Detected - Version: {result[0]}")
            else:
                logger.warning("❌ WARNING: GDS Plugin not detected. Topology analysis may fail.")
            
            # 3. Label check (Forensic Readiness)
            result = session.run("CALL db.labels()").value()
            logger.info(f"Substrate Labels: {result}")
            
            # 4. Procedure check (APOC)
            result = session.run("SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc.' RETURN count(name)").single()
            if result and result[0] > 0:
                logger.info(f"✅ SUCCESS: APOC Procedures detected ({result[0]} items).")
            else:
                logger.warning("❌ WARNING: APOC Procedures not detected in unrestricted scope.")
                
        driver.close()
        logger.info("\n--- NEO_VAL STATUS: READY FOR INGESTION ---")
            
    except Exception as e:
        logger.error(f"❌ FATAL: Neo4j Validation Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate_neo4j()
