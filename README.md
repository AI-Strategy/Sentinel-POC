# Sentinel — Ghost Invoice Detection System

A graph-based "data substrate" that decouples enterprise data from apps. Ingest dirty Invoice (JSON), PO (CSV), POD (XML); stitch into Transaction objects; detect price/qty/phantom line leaks; emit claim-ready evidence reports w/ file+line traceability.

## 🏗 Architecture Components

### 1. Backend (FastAPI + Neo4j)
Located in `/backend`. Uses the **Liquid** core for fuzzy matching and ghost detection.
- **Start**: 
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  ```

### 2. Relational Substrate (Postgres local)
Located in root. Used for metadata and transaction state.
- **Start**:
  ```bash
  docker-compose up -d
  ```

### 3. Frontend (React + Tailwind + Vite)
Located in `/frontend`. Premium dashboard for visualizing leakage and graph topologies.
- **Start**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

### 3. MCP Bifrost (Model Context Protocol)
Located in `/mcp`. Bridge between LLMs and the Neo4j substrate.
- **Registration**: Add this to your `mcp.json` or equivalent agent config:
  ```json
  {
    "mcpServers": {
      "bifrost": {
        "command": "python",
        "args": ["d:/Projects/Sentinel/repo/Sentinel-POC/mcp/bifrost.py"],
        "env": {
          "NEO4J_URI": "bolt://localhost:7687",
          "NEO4J_USERNAME": "neo4j",
          "NEO4J_PASSWORD": "password"
        }
      }
    }
  }
  ```

## 🔐 Environment
The system expects:
- **Neo4j Aura**: (`neo4j+s://...`) for the graph substrate. Update `.env`.
- **Postgres local**: (`localhost:5432`) for relational storage.
- **MCP Bifrost**: Active bridge for natural language to Cypher.
