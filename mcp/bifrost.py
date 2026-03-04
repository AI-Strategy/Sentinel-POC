"""
mcp/bifrost.py
--------------
Bifrost bridge between LLMs and Neo4j.
Provides tools to query the Sentinel graph substrate using Cypher.
"""

import os
from mcp.server import Server, NotificationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")

server = Server("bifrost-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_graph",
            description="Execute a Cypher query against the Sentinel Neo4j graph.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The Cypher query to execute."},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_graph_schema",
            description="Retrieve labels and relationship types from the graph.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if name == "get_graph_schema":
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
            with driver.session() as session:
                labels = session.run("CALL db.labels()").value()
                rels = session.run("CALL db.relationshipTypes()").value()
                return [TextContent(type="text", text=f"Labels: {labels}\nRelationships: {rels}")]

    if name == "query_graph":
        query = arguments.get("query")
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)) as driver:
            with driver.session() as session:
                result = session.run(query)
                data = [record.data() for record in result]
                return [TextContent(type="text", text=str(data))]

    raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    # Standard MCP stdio transport for local use
    from mcp.server.stdio import stdio_server
    import asyncio
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
            
    asyncio.run(main())
