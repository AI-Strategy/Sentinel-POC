import os
import sys
from dotenv import load_dotenv

def check_env():
    load_dotenv()
    neo_uri = os.getenv("NEO4J_URI", "")
    neo_pass = os.getenv("NEO4J_PASSWORD", "")
    pg_url = os.getenv("DATABASE_URL", "")

    print(f"--- Environment Configuration ---")
    print(f"NEO4J_URI: {neo_uri}")
    print(f"DATABASE_URL: {pg_url}")
    
    if "<YOUR_AURA_" in neo_uri or "<YOUR_AURA_" in neo_pass:
        print("\n[!] WARNING: Neo4j Aura placeholders detected. Update your .env file with actual credentials.")
        return False
    return True

def verify_neo4j():
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pw = os.getenv("NEO4J_PASSWORD")
    
    print(f"\n--- Verifying Neo4j Aura Connection ({uri}) ---")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pw))
        with driver.session() as session:
            session.run("RETURN 1")
        print("[SUCCESS] Neo4j Connection")
        driver.close()
        return True
    except Exception as e:
        print(f"[FAILED] Neo4j Connection\n   Error: {e}")
        return False

def verify_postgres():
    from sqlalchemy import create_engine
    url = os.getenv("DATABASE_URL")
    
    print(f"\n--- Verifying Postgres Connection ({url}) ---")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("[SUCCESS] Postgres Connection")
        return True
    except Exception as e:
        print(f"[FAILED] Postgres Connection\n   Error: {e}")
        return False

if __name__ == "__main__":
    if not check_env():
        sys.exit(1)
        
    try:
        neo_ok = verify_neo4j()
    except ImportError:
        print("\n[!] Missing 'neo4j' library. Run 'pip install neo4j'")
        neo_ok = False
        
    try:
        pg_ok = verify_postgres()
    except ImportError:
        print("\n[!] Missing 'sqlalchemy' or 'psycopg2' library. Run 'pip install sqlalchemy psycopg2-binary'")
        pg_ok = False
        
    if neo_ok and pg_ok:
        print("\n[SUCCESS] All systems operational. Substrate is ready.")
        sys.exit(0)
    else:
        print("\n[WARNING] Connection verification failed for one or more databases.")
        sys.exit(1)
