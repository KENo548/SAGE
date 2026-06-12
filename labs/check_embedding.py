import requests, time

url = 'http://localhost:11434'

start = time.time()
r = requests.post(
    f'{url}/api/embeddings',
    json={'model': 'nomic-embed-text:latest', 'prompt': 'test embedding call'},
    timeout=120
)
elapsed = time.time() - start

print(f'Status: {r.status_code}')
print(f'Time: {elapsed:.2f}s')
data = r.json()
vec = data['embedding']
print(f'Vector dim: {len(vec)}')
print(f'First 5: {vec[:5]}')
print(f'Min: {min(vec):.6f} Max: {max(vec):.6f}')
print(f'Norm: {sum(x*x for x in vec)**0.5:.4f}')
