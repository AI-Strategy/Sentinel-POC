from neo4j import GraphDatabase
import sys

def check_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "sentinel_neo4j"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Check labels
            result = session.run("MATCH (n) RETURN labels(n) as label, count(*) as count")
            data = result.data()
            print("--- Neo4j Node Counts ---")
            if not data:
                print("No nodes found in the graph.")
            for row in data:
                print(f"Label: {row['label']}, Count: {row['count']}")
            
            # Check relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(*) as count")
            data = result.data()
            print("\n--- Neo4j Relationship Counts ---")
            for row in data:
                print(f"Type: {row['type']}, Count: {row['count']}")
            
            # Check for specific GhostFlags
            result = session.run("MATCH (g:GhostFlag) RETURN g.ghost_type as type, count(*) as count")
            data = result.data()
            print("\n--- GhostFlag Breakdown ---")
            for row in data:
                print(f"Type: {row['type']}, Count: {row['count']}")
                
            # Check for evidentiary links
            result = session.run("MATCH (g:GhostFlag)-[r:EVIDENCE_FROM]->(s) RETURN count(r) as link_count")
            count = result.single()["link_count"]
            print(f"\nEvidentiary Links: {count}")
            
        driver.close()
    except Exception as e:
        print(f"FAILED to connect to Neo4j: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_neo4j()
