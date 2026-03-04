---
name: neo4j-deep-architect
description: Master skill for Neo4j 5.x+, GDS, Vector Indexing, and Bulk Ingestion.
---

# Neo4j Expert Protocol

## 1. Native Vector Support (Neo4j 5.x+)
- **Data Type**: Use the native `VECTOR<FLOAT32>` type. Do not store embeddings as generic `LIST<FLOAT>`.
- **Indexing**:
  - Create standard Vector Indexes: `CREATE VECTOR INDEX ... OPTIONS {indexConfig: {vector.dimensions: 1536, vector.similarity_function: 'cosine'}}`.
  - **Query**: Use `db.index.vector.queryNodes()`.
- **Hybrid Search**: Combine Vector Search with Full-Text Indexes using `neo4j-graphrag` HybridRetriever for best results.

## 2. Graph Data Science (GDS)
- **Client**: Use the official `graphdatascience` Python client.
- **Projection**: Prefer **Native Projections** (`gds.graph.project`) over Cypher Projections for memory efficiency.
- **Memory**: Always run `gds.graph.project.estimate()` before projecting a massive graph.

## 3. High-Performance Ingestion
- **Bulk**: Use `neo4j-admin database import` for initial loads (>10M nodes).
- **Incremental**: Use `LOAD CSV` with `CALL { ... } IN TRANSACTIONS OF 1000 ROWS` to prevent memory blowouts.
- **Deadlock Avoidance**: When loading relationships in parallel, sort by `startNode` ID to minimize locking conflicts.

## 4. Cypher Standards
- **Parameters**: STRICT usage of `$params`. No string concatenation.
- **Labels**: Always specify labels in matches (`MATCH (n:Person)`), never generic `MATCH (n)`.
