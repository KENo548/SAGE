# labs/test_pipeline.py
import yaml
import requests
import numpy as np

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_embeddings(texts, model, url):
    embeddings = []
    for text in texts:
        try:
            res = requests.post(
                f"{url}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=60
            )
            if res.status_code == 200:
                embeddings.append(res.json()["embedding"])
            else:
                embeddings.append(list(np.random.uniform(-1, 1, 768)))
        except Exception:
            embeddings.append(list(np.random.uniform(-1, 1, 768)))
    return embeddings

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def generate_candidate_summary(cluster_texts, model, url):
    prompt = f"""
The user has made the following statements in past conversations:
{chr(10).join('- ' + text for text in cluster_texts)}

Synthesize these statements into one concise, clear first-person preference belief statement (e.g., 'User prefers...', 'User dislikes...').
Output ONLY the synthesized statement, nothing else.
"""
    system_prompt = "You are a precise summarization engine."
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.0}
    }
    try:
        res = requests.post(f"{url}/api/generate", json=payload, timeout=60)
        return res.json().get("response", "").strip().strip('"')
    except Exception as e:
        return f"Error summarizing cluster: {str(e)}"

def test_knowledge_promotion_pipeline():
    print("=== Starting Knowledge Promotion Pipeline Sandbox ===")
    config = load_yaml("labs/config.yaml")
    ollama_url = config["models"]["ollama_url"]
    embed_model = config["models"]["embedding"]
    llm_model = config["models"]["primary"]
    
    # Input episodic memories stream
    memories = [
        # Cluster A: Afternoon meetings
        {"id": "m1", "text": "Hart rescheduled the morning meeting to 11 AM.", "type": "A_candidate"},
        {"id": "m2", "text": "Hart noted that morning meetings before 10 AM disrupt his flow.", "type": "A_candidate"},
        {"id": "m3", "text": "Hart mentioned he prefers all scrum calls to be in the afternoon.", "type": "A_candidate"},
        # Cluster B: Python formatter
        {"id": "m4", "text": "Hart wants python scripts formatted with black.", "type": "A_candidate"},
        {"id": "m5", "text": "Hart prefers black formatter for python projects.", "type": "A_candidate"},
        {"id": "m6", "text": "Hart likes the black python style.", "type": "A_candidate"},
        # Type B: Direct assertions
        {"id": "m7", "text": "My primary email is hart@example.com", "type": "B_fact"},
        {"id": "m8", "text": "Actually, I changed my primary email to hart.dev@example.com", "type": "B_fact"},
        # Noise
        {"id": "m9", "text": "Hart logged in.", "type": "noise"},
        {"id": "m10", "text": "System checked rules.", "type": "noise"},
        {"id": "m11", "text": "Hart closed the session.", "type": "noise"}
    ]
    
    print(f"Loaded {len(memories)} test memories.")
    
    # Step 1: Handle Type B facts (Direct assertion pipeline)
    print("\n--- Running Type B Direct Fact Pipeline ---")
    type_b_store = {}
    
    for mem in memories:
        text = mem["text"]
        # Detect Type B direct assertions (simple regex match for prototype)
        match = re.search(r"primary email is ([\w\.-]+@[\w\.-]+)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"primary email to ([\w\.-]+@[\w\.-]+)", text, re.IGNORECASE)
            
        if match:
            email = match.group(1)
            print(f"Detected Type B Fact: Primary Email -> {email}")
            
            # De-activate previous records (Law 7)
            for fact_id, fact in list(type_b_store.items()):
                if fact["key"] == "primary_email" and fact["status"] == "active":
                    type_b_store[fact_id]["status"] = "superseded"
                    type_b_store[fact_id]["superseded_by"] = f"fact_email_{email}"
                    print(f"  -> Superseded old fact: {fact['value']}")
            
            type_b_store[f"fact_email_{email}"] = {
                "key": "primary_email",
                "value": email,
                "status": "active",
                "source_memory": mem["id"]
            }
            
    # Verify Type B state
    print("\nType B Store Final State:")
    for fid, f in type_b_store.items():
        print(f"  [{fid}] Status: {f['status']} | Value: {f['value']}")
        
    # Step 2: Semantic Clustering (Type A candidates pipeline)
    print("\n--- Running Type A Candidate Promotion Pipeline ---")
    
    # Filter out memories that went to Type B and get embeddings for the rest
    remaining_mems = [m for m in memories if m["type"] != "B_fact"]
    texts = [m["text"] for m in remaining_mems]
    
    print("Embedding remaining memories...")
    embeddings = get_embeddings(texts, embed_model, ollama_url)
    
    # Simple single-linkage clustering threshold
    similarity_threshold = 0.65
    clusters = []
    visited = set()
    
    for i in range(len(remaining_mems)):
        if i in visited:
            continue
        # Start a new cluster
        cluster = [i]
        visited.add(i)
        
        for j in range(i + 1, len(remaining_mems)):
            if j in visited:
                continue
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim >= similarity_threshold:
                cluster.append(j)
                visited.add(j)
        clusters.append(cluster)
        
    # Process clusters and check promotion
    promoted_candidates = []
    false_promoted_count = 0
    missed_promoted_count = 2 # We expect 2 clusters (meetings, black formatter)
    
    print("\nClustering Results:")
    for idx, c in enumerate(clusters):
        cluster_mems = [remaining_mems[i] for i in c]
        cluster_texts = [m["text"] for m in cluster_mems]
        print(f"  Cluster {idx+1} (Size: {len(c)}):")
        for m in cluster_mems:
            print(f"    - [{m['type']}] {m['text']}")
            
        # Promotion threshold: cluster size >= 3
        if len(c) >= 3:
            print(f"  -> Cluster size >= 3: Triggering LLM promotion...")
            summary = generate_candidate_summary(cluster_texts, llm_model, ollama_url)
            print(f"  Candidate Statement: '{summary}'")
            promoted_candidates.append({
                "statement": summary,
                "source_mems": [m["id"] for m in cluster_mems]
            })
            
            # Evaluate metrics
            # If the cluster is primarily noise, it is a false promotion
            types = [m["type"] for m in cluster_mems]
            if types.count("noise") > len(c) / 2:
                false_promoted_count += 1
                
            # If it is one of our expected classes, decrement missed counts
            if any(t == "A_candidate" for t in types):
                missed_promoted_count -= 1
        else:
            print(f"  -> Retained as episodic only (size < 3)")
            
    # Calculate Precision Metrics
    total_promotions = len(promoted_candidates)
    false_promotion_rate = false_promoted_count / total_promotions if total_promotions > 0 else 0.0
    missed_promotion_rate = max(0, missed_promoted_count) / 2.0  # 2 expected promotions
    
    print("\nKnowledge Pipeline Metrics:")
    print(f"  - Total Candidates Promoted: {total_promotions}")
    print(f"  - False Promotion Rate: {false_promotion_rate * 100:.1f}% (Target: 0%)")
    print(f"  - Missed Promotion Rate: {missed_promotion_rate * 100:.1f}% (Target: 0%)")
    
    return {
        "total_promotions": total_promotions,
        "false_promotion_rate": false_promotion_rate,
        "missed_promotion_rate": missed_promotion_rate
    }

import re
if __name__ == "__main__":
    test_knowledge_promotion_pipeline()
