import yaml, requests, numpy as np
from itertools import combinations

with open('labs/config.yaml') as f:
    config = yaml.safe_load(f)

url = config['models']['ollama_url']
embed_model = config['models']['embedding']


def get_embedding(text):
    r = requests.post(
        f'{url}/api/embeddings',
        json={'model': embed_model, 'prompt': text},
        timeout=60
    )
    return r.json()['embedding']


def cosine_sim(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


# Pipeline test memories
memories = [
    ('M1', 'Hart rescheduled the morning meeting to 11 AM.'),
    ('M2', 'Hart noted that morning meetings before 10 AM disrupt his flow.'),
    ('M3', 'Hart mentioned he prefers all scrum calls to be in the afternoon.'),
    ('M4', 'Hart wants python scripts formatted with black.'),
    ('M5', 'Hart prefers black formatter for python projects.'),
    ('M6', 'Hart likes the black python style.'),
    ('N1', 'Hart logged in.'),
    ('N2', 'System checked rules.'),
    ('N3', 'Hart closed the session.'),
]

print(f'Embedding model: {embed_model}')
print(f'Getting embeddings for {len(memories)} memories...')
embeddings = {id_: get_embedding(text) for id_, text in memories}
dim = len(list(embeddings.values())[0])
print(f'Embedding dimension: {dim}')
print()

# Full matrix
ids = [m[0] for m in memories]
print('Similarity Matrix:')
header = ''.join(f'{id_:>10}' for id_ in ids)
print(f'{"":>10}{header}')
for id1 in ids:
    row = f'{id1:>10}'
    for id2 in ids:
        sim = cosine_sim(embeddings[id1], embeddings[id2])
        row += f'{sim:>10.4f}'
    print(row)
print()

# Same-topic pairs
same_topic = {
    'Meetings': [('M1', 'M2'), ('M1', 'M3'), ('M2', 'M3')],
    'Black formatter': [('M4', 'M5'), ('M4', 'M6'), ('M5', 'M6')],
    'Noise vs noise': [('N1', 'N2'), ('N1', 'N3'), ('N2', 'N3')],
}

print('Within-group similarities:')
for group, pairs in same_topic.items():
    sims = [cosine_sim(embeddings[a], embeddings[b]) for a, b in pairs]
    print(f'  {group}: min={min(sims):.4f} avg={np.mean(sims):.4f} max={max(sims):.4f}')
print()

# Cross-topic pairs
cross_pairs = [('M1', 'M4'), ('M1', 'N1'), ('M3', 'N3'), ('M4', 'N1'), ('M6', 'N2')]
cross_sims = [cosine_sim(embeddings[a], embeddings[b]) for a, b in cross_pairs]
print('Cross-group similarities:')
for (a, b), sim in zip(cross_pairs, cross_sims):
    print(f'  {a} vs {b}: {sim:.4f}')
print(f'  range: {min(cross_sims):.4f} - {max(cross_sims):.4f}')
print()

# Same-topic vs different-topic distribution
same_vals = []
for group, pairs in same_topic.items():
    same_vals.extend([cosine_sim(embeddings[a], embeddings[b]) for a, b in pairs])

all_ids = list(range(len(memories)))
cross_vals = []
for i, j in combinations(range(len(memories)), 2):
    id1, id2 = ids[i], ids[j]
    is_same = False
    for pairs in same_topic.values():
        if (id1, id2) in pairs or (id2, id1) in pairs:
            is_same = True
            break
    if not is_same:
        cross_vals.append(cosine_sim(embeddings[id1], embeddings[id2]))

print('Distribution:')
print(f'  Same-topic:  min={min(same_vals):.4f} median={np.median(same_vals):.4f} mean={np.mean(same_vals):.4f} max={max(same_vals):.4f}')
print(f'  Cross-topic: min={min(cross_vals):.4f} median={np.median(cross_vals):.4f} mean={np.mean(cross_vals):.4f} max={max(cross_vals):.4f}')
print()

# Threshold sweep
print('Threshold sweep:')
for thresh in [0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35]:
    visited = set()
    clusters = []
    for i in range(len(memories)):
        if i in visited:
            continue
        cluster = [i]
        visited.add(i)
        for j in range(i + 1, len(memories)):
            if j in visited:
                continue
            sim = cosine_sim(embeddings[ids[i]], embeddings[ids[j]])
            if sim >= thresh:
                cluster.append(j)
                visited.add(j)
        clusters.append(cluster)
    cluster_sizes = [len(c) for c in clusters]
    print(f'  threshold={thresh:.2f} -> {len(clusters)} clusters, sizes={sorted(cluster_sizes, reverse=True)}')

# Normalized versions test
print()
print('=== Normalized text test ===')
raw_vs_normalized = [
    ('Raw', 'Hart avoids meetings before 10am.'),
    ('Norm', 'User preference: avoid meetings before 10am.'),
]
for label, text in raw_vs_normalized:
    e = get_embedding(text)
    sim_to_m1 = cosine_sim(e, embeddings['M1'])
    sim_to_m2 = cosine_sim(e, embeddings['M2'])
    sim_to_m3 = cosine_sim(e, embeddings['M3'])
    sim_to_m4 = cosine_sim(e, embeddings['M4'])
    print(f'  {label}: "{text}"')
    print(f'    sim to M1(meeting): {sim_to_m1:.4f}')
    print(f'    sim to M2(meeting): {sim_to_m2:.4f}')
    print(f'    sim to M3(meeting): {sim_to_m3:.4f}')
    print(f'    sim to M4(black):  {sim_to_m4:.4f}')
