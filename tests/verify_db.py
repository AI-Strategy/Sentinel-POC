"""
sentinel/tests/verify_db.py
---------------------------
Validates the Neo4j database connection and credentials prior to batch processing.
"""

import os
import sys
import logging
from neo4j import GraphDatabase, exceptions

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("sentinel.verify")

def verify_connection() -> int:
    # Default to localhost if environment variables are unset
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "sentinel_neo4j")

    logger.info("Attempting connection to Neo4j at %s as user '%s'...", uri, user)
    
    try:
        # Initialize the driver using the 6.1.0 specification
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Explicitly verify the connection state
        driver.verify_connectivity()
        logger.info("✅ Connection successful. The Neo4j database is accessible and ready.")
        
        driver.close()
        return 0
        
    except exceptions.AuthError:
        logger.error("❌ Authentication failed. Verify NEO4J_USERNAME and NEO4J_PASSWORD.")
        return 1
    except exceptions.ServiceUnavailable:
        logger.error("❌ Service unavailable. Verify that Neo4j is running at %s and the port is accessible.", uri)
        return 1
    except Exception as e:
        logger.error("❌ Connection failed: %s", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(verify_connection())
