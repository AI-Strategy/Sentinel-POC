"""
mcp/bifrost.py
--------------
Bifrost bridge between LLMs and the Sentinel substrate (Neo4j + Postgres).
Provides tools to query both graph and relational data.
"""

import os
import sys
import asyncio
import logging
import psycopg2
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Configuration
SENTINEL_AUTH_KEY = os.getenv("SENTINEL_AUTH_KEY")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")

POSTGRES_DB = os.getenv("POSTGRES_DB", "sentinel")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

if not SENTINEL_AUTH_KEY:
    print("FATAL: SENTINEL_AUTH_KEY is not set. MCP Bifrost requires authentication.", file=sys.stderr)
    sys.exit(1)

server = Server("bifrost-mcp")

# ── Tool Definitions ──────────────────────────────────────────────────────────

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        # Neo4j Tools
        Tool(
            name="query_neo4j",
            description="Execute a Cypher query against the Sentinel Neo4j graph substrate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The Cypher query to execute."},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_neo4j_schema",
            description="Retrieve labels and relationship types from the Neo4j graph.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # Postgres Tools
        Tool(
            name="query_postgres",
            description="Execute a SQL query against the Sentinel Postgres relational substrate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "The SQL query to execute."},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_postgres_schema",
            description="Retrieve table names and column definitions from Postgres.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

# ── Tool Handlers ─────────────────────────────────────────────────────────────

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    # ── Neo4j Handlers ──
    if name == "get_neo4j_schema":
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
            with driver.session() as session:
                labels = session.run("CALL db.labels()").value()
                rels = session.run("CALL db.relationshipTypes()").value()
                return [TextContent(type="text", text=f"Labels: {labels}\nRelationships: {rels}")]

    if name == "query_neo4j":
        query = arguments.get("query")
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
            with driver.session() as session:
                result = session.run(query)
                data = [record.data() for record in result]
                return [TextContent(type="text", text=str(data))]

    # ── Postgres Handlers ──
    if name == "get_postgres_schema":
        conn = psycopg2.connect(
            dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASS,
            host=POSTGRES_HOST, port=POSTGRES_PORT
        )
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name, column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """)
                schema = cur.fetchall()
                formatted = "\n".join([f"{row[0]}.{row[1]} ({row[2]})" for row in schema])
                return [TextContent(type="text", text=f"Postgres Schema (public):\n{formatted}")]
        finally:
            conn.close()

    if name == "query_postgres":
        sql = arguments.get("sql")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASS,
            host=POSTGRES_HOST, port=POSTGRES_PORT
        )
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    data = [dict(zip(columns, row)) for row in cur.fetchall()]
                    return [TextContent(type="text", text=str(data))]
                else:
                    conn.commit()
                    return [TextContent(type="text", text="Query executed successfully (no results).")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing Postgres query: {str(e)}")]
        finally:
            conn.close()

    raise ValueError(f"Unknown tool: {name}")

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
            
    asyncio.run(main())
