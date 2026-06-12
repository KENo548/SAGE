import chromadb, yaml

with open('labs/config.yaml') as f:
    config = yaml.safe_load(f)

db_path = config['memory']['db_path']
print(f'ChromaDB path: {db_path}')

client = chromadb.PersistentClient(path=db_path)
collections = client.list_collections()
print(f'Collections: {[c.name for c in collections]}')

# Check the ambiguity collection
try:
    coll = client.get_collection('ambiguity_collection')
    print(f'\nAmbiguity collection metadata: {coll.metadata}')
    print(f'Count: {coll.count()}')
    
    # Query with a test
    results = coll.query(query_texts=['coffee'], n_results=3)
    for doc, dist in zip(results['documents'][0], results['distances'][0]):
        print(f'  dist={dist:.2f} | {doc}')
except Exception as e:
    print(f'Error: {e}')
