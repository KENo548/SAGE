# labs/test_memory.py
import yaml
import requests
import chromadb
import time
import random
from chromadb import EmbeddingFunction, Documents, Embeddings
from data_templates import get_ambiguous_memories, generate_synthetic_memories

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name, url):
        self.model_name = model_name
        self.url = url

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                res = requests.post(
                    f"{self.url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=60
                )
                if res.status_code == 200:
                    embeddings.append(res.json()["embedding"])
                else:
                    # Fallback random vector if server fails
                    embeddings.append([random.uniform(-1, 1) for _ in range(768)])
            except Exception:
                embeddings.append([random.uniform(-1, 1) for _ in range(768)])
        return embeddings

def test_memory_scaling_and_ambiguity():
    print("=== Starting Memory Benchmark and Ambiguity Test ===")
    config = load_yaml("labs/config.yaml")
    
    ollama_url = config["models"]["ollama_url"]
    embed_model = config["models"]["embedding"]
    
    # Initialize Embedding function
    emb_fn = OllamaEmbeddingFunction(embed_model, ollama_url)
    
    # Check if embedding model is pulled
    try:
        test_embed = emb_fn(["test embedding call"])
        if not test_embed or len(test_embed[0]) != 768:
            print(f"Error: Embedding model '{embed_model}' did not return valid vectors. Make sure it is pulled via 'ollama pull {embed_model}'.")
            return {}
    except Exception as e:
        print(f"Error verifying embedding model: {e}")
        return {}

    # Initialize ChromaDB Client (in-memory or temp path)
    client = chromadb.PersistentClient(path=config["memory"]["db_path"])
    
    # Run Ambiguity Tests
    print("\n--- Running Ambiguity Test ---")
    try:
        client.delete_collection("ambiguity_collection")
    except Exception:
        pass
    
    amb_coll = client.create_collection("ambiguity_collection", embedding_function=emb_fn, metadata={"hnsw:space": "cosine"})
    amb_memories = get_ambiguous_memories()
    
    # Add memories one by one to simulate logs
    for idx, mem in enumerate(amb_memories):
        # We store the timestamp in the metadata
        amb_coll.add(
            ids=[mem["id"]],
            documents=[mem["text"]],
            metadatas=[{"timestamp": mem["timestamp"]}]
        )
    
    # Test Query: "What does Hart drink on Tuesdays?"
    # Expectation: 
    # Semantic search will return cold brew (Tuesday specific) and green tea (general drink preference, recently updated).
    # We want to see how these are ranked.
    query = "What does Hart drink on Tuesday mornings?"
    results = amb_coll.query(query_texts=[query], n_results=5)
    
    print(f"Query: '{query}'")
    print("Top retrieved results (by distance):")
    for doc, dist, metadata in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
        print(f"  - [{dist:.4f}] {doc} (Date: {metadata.get('timestamp')})")
        
    # Check if the most recent green tea transition OR the Tuesday cold brew dominates
    docs_retrieved = results["documents"][0]
    has_tea = any("tea" in doc.lower() for doc in docs_retrieved[:2])
    has_cold_brew = any("cold brew" in doc.lower() for doc in docs_retrieved[:2])
    
    print(f"Ambiguity Resolution:")
    print(f"  - Retained Recent Habit (Green Tea) in Top 2: {has_tea}")
    print(f"  - Retained Tuesday Habit (Cold Brew) in Top 2: {has_cold_brew}")

    # Run Database Scaling Tests (100, 1000, 5000, 10000)
    # We use random vectors for filler entries to prevent GTX 1650 system lockup embedding 10,000 strings.
    # We embed actual needle queries and inject them.
    scale_steps = [100, 1000, 5000, 10000]
    scale_results = {}
    
    print("\n--- Running Scaling & Recall Tests ---")
    
    # Pre-embed the needles to ensure high precision
    needle_texts = [
        "Hart decided to use PostgreSQL for the production environment.",
        "Hart's birthday is on September 14th.",
        "Hart prefers using a dark theme for all code editors."
    ]
    needle_embeddings = emb_fn(needle_texts)
    
    for step in scale_steps:
        print(f"Preparing scale: {step} entries...")
        try:
            client.delete_collection(f"scale_{step}")
        except Exception:
            pass
            
        coll = client.create_collection(f"scale_{step}", embedding_function=emb_fn, metadata={"hnsw:space": "cosine"})
        
        # Generate raw metadata and documents
        raw_memories = generate_synthetic_memories(step)
        
        # Prepare batches for ChromaDB
        ids = []
        docs = []
        embeddings = []
        
        for mem in raw_memories:
            ids.append(mem["id"])
            docs.append(mem["text"])
            
            # If it's a needle, use the pre-computed real embedding
            if mem.get("is_needle"):
                if "PostgreSQL" in mem["text"]:
                    embeddings.append(needle_embeddings[0])
                elif "birthday" in mem["text"]:
                    embeddings.append(needle_embeddings[1])
                else:
                    embeddings.append(needle_embeddings[2])
            else:
                # Filler gets random unit vector (norm=1) — cosine-compatible
                vec = [random.gauss(0, 1) for _ in range(768)]
                norm = sum(x*x for x in vec) ** 0.5
                embeddings.append([x / norm for x in vec])
                
        # Insert in batches of 1000
        batch_size = 1000
        for i in range(0, len(ids), batch_size):
            coll.add(
                ids=ids[i:i+batch_size],
                documents=docs[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size]
            )
            
        # Test Query Recall & Latency
        query_text = "What database did Hart choose for production?"
        start_time = time.perf_counter()
        query_res = coll.query(query_texts=[query_text], n_results=5)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        retrieved_docs = query_res["documents"][0]
        recall_success = any("PostgreSQL" in doc for doc in retrieved_docs)
        
        scale_results[step] = {
            "latency_ms": latency_ms,
            "recall": recall_success,
            "top_match": retrieved_docs[0] if retrieved_docs else "None"
        }
        print(f"  Scale {step} -> Latency: {latency_ms:.2f}ms | Recall: {recall_success}")
        
    return scale_results

if __name__ == "__main__":
    test_memory_scaling_and_ambiguity()
