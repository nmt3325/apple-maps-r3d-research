import json
from pathlib import Path
p=Path('/opt/flyover-viewer/www/data/native-c3m.json')
data=json.loads(p.read_text())
print(data['originalPolygonTileCount'],data['totalTriangles'])
from collections import Counter
counts=Counter()
for tile in data['tiles']:
 counts[tile['z']]+=1
 assert tile['triangles']>0
 assert tile['vertices']>0
 assert tile['originalUV']>0
 assert tile['originalNormals']>0
print('zoom tiers',dict(counts))
assert sum(t['triangles'] for t in data['tiles'])==data['totalTriangles']
assert sum(t['vertices'] for t in data['tiles'])==data['combinedUniqueVertices']
print('PASS manifest totals')
