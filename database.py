import os
import psycopg2
from typing import Optional
import chromadb
from chromadb.config import Settings
from langchain_core.tools import tool

def get_db_connection(db_url: str):
    """Simple wrapper for PostgreSQL connection."""
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_chroma_client(persist_path: str):
    """Simple wrapper for ChromaDB client."""
    client = chromadb.PersistentClient(path=persist_path)
    return client

def init_databases(postgres_url: Optional[str], chroma_path: str):
    """Initialize folders and check connections."""
    os.makedirs(chroma_path, exist_ok=True)
    os.makedirs("knowledge", exist_ok=True)
    
    if postgres_url:
        conn = get_db_connection(postgres_url)
        if conn:
            print("PostgreSQL connection verified.")
            conn.close()
    
    print(f"ChromaDB initialized at {chroma_path}")

@tool
def query_memory(query: str, n_results: int = 3):
    """
    Search long-term vector database memory for related knowledge.
    Returns the most relevant contexts related to the query.
    """
    try:
        client = get_chroma_client("./chroma_db")
        collection = client.get_or_create_collection("agent_memory")
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if hasattr(results, 'get') and results.get("documents") and results["documents"][0]:
            return "Found relevant past memory:\n" + "\n---\n".join(results["documents"][0])
        else:
            return "No relevant memories found."
    except Exception as e:
        return f"Error querying database: {str(e)}"
