#!/usr/bin/env python3
"""
Query L2 graph for docs and IMPLEMENTS relationships
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load credentials
load_dotenv('.env.l2_resolver')

API_URL = os.getenv('FALKORDB_API_URL')
API_KEY = os.getenv('FALKORDB_API_KEY')
GRAPH_NAME = 'scopelock'  # Querying scopelock graph

if not API_URL or not API_KEY:
    print("Error: FALKORDB_API_URL and FALKORDB_API_KEY required")
    exit(1)

# Cypher query: Find all knowledge objects (docs) and what they implement
QUERY = """
MATCH (ko:U4_Knowledge_Object)-[r:U4_IMPLEMENTS]->(target)
RETURN ko.name AS doc_name,
       ko.ko_type AS doc_type,
       ko.path AS doc_path,
       labels(target)[0] AS target_type,
       target.name AS target_name,
       target.path AS target_path
ORDER BY ko.name
LIMIT 100
"""

def query_graph(cypher: str):
    """Execute Cypher query against FalkorDB"""
    payload = {
        "graph_name": GRAPH_NAME,
        "query": cypher,
        "params": {}
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()

        if "data" in result and "result" in result["data"]:
            return result["data"]["result"]

        return []

    except Exception as e:
        print(f"Query failed: {e}")
        raise

if __name__ == "__main__":
    print(f"Querying graph '{GRAPH_NAME}' for docs and IMPLEMENTS relationships...\n")

    try:
        rows = query_graph(QUERY)

        if not rows:
            print("No results found")
        else:
            print(f"Found {len(rows)} doc → implementation relationships:\n")

            for row in rows:
                doc_name = row[0]
                doc_type = row[1]
                doc_path = row[2]
                target_type = row[3]
                target_name = row[4]
                target_path = row[5]

                print(f"📄 {doc_name} ({doc_type})")
                print(f"   Path: {doc_path}")
                print(f"   IMPLEMENTS → {target_type}: {target_name}")
                print(f"   Path: {target_path}")
                print()

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
