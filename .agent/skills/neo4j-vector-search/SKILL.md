---
name: neo4j-vector-search
description: Performs a semantic vector search against the GraphRAG memory.
---

# Neo4j Vector Search

## Goal
Retrieve context from the "Deep" memory layer using vector embeddings.

## Constraints
1.  **Dimensions**: Must explicitly check index dimensions (e.g., 1536 for OpenAI).
2.  **Cypher Safety**: Use parameters `{embedding}`, NEVER string formatting.

## Template (Cypher)
```cypher
CALL db.index.vector.queryNodes('my_vector_index', 10, $embedding)
YIELD node, score
RETURN node.content, score
WHERE score > 0.8
