import os
import psycopg
from typing import Optional
from urllib.parse import urlsplit
import chromadb
from chromadb.config import Settings
from langchain_core.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver

def get_db_connection(db_url: str):
    """Simple wrapper for PostgreSQL connection."""
    try:
        conn = psycopg.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_db_if_not_exists(postgres_url: str):
    """Check if database exists, create it using the default 'postgres' database if it doesn't."""
    parsed = urlsplit(postgres_url)
    db_name = parsed.path.lstrip('/')
    
    # Connect to the default 'postgres' database to check/create the target database
    base_url = postgres_url.replace(f"/{db_name}", "/postgres")
    try:
        with psycopg.connect(base_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cur.fetchone()
                if not exists:
                    print(f"Database '{db_name}' does not exist. Creating it...")
                    cur.execute(f'CREATE DATABASE "{db_name}"')
                    print(f"Database '{db_name}' created successfully.")
    except Exception as e:
        print(f"Could not check or create database '{db_name}': {e}")

def get_chroma_client(persist_path: str):
    """Simple wrapper for ChromaDB client."""
    client = chromadb.PersistentClient(path=persist_path)
    return client

def init_databases(postgres_url: Optional[str], chroma_path: str):
    """Initialize folders, check connections, and setup checkpointer tables."""
    os.makedirs(chroma_path, exist_ok=True)
    os.makedirs("knowledge", exist_ok=True)
    
    if postgres_url:
        create_db_if_not_exists(postgres_url)
        conn = get_db_connection(postgres_url)
        if conn:
            print("PostgreSQL connection verified.")
            conn.close()
            # Setup tables for checkpointer
            with PostgresSaver.from_conn_string(postgres_url) as checkpointer:
                checkpointer.setup()
    
    print(f"ChromaDB initialized at {chroma_path}")

def get_query_memory_tool(vector_db_path: str):
    @tool
    def query_memory(query: str, n_results: int = 3):
        """
        Search long-term vector database memory for related knowledge.
        Returns the most relevant contexts related to the query.
        """
        try:
            client = get_chroma_client(vector_db_path)
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
    
    return query_memory
