"""Check a real simulator run, independent of the rendering implementation."""
import json
import statistics
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
samples = report['samples']
assert len(samples) == 121 and samples[-1]['second'] == 120
assert report['signatureMatchesPython'] is True
assert max(s['pending'] for s in samples) <= 2
assert all(s['residentBytes'] <= s['budget'] for s in samples)
assert max(s['failures'] for s in samples) == 0
assert any(s['latitude'] == 21.2828 and s['drawnTiles'] > 0 for s in samples)
assert any(s['eye'][0] == 450 and s['drawnTiles'] > 0 for s in samples)
assert {18,19,20}.issubset({z for s in samples for z in s['visibleLODs']})
assert any(h > 0 for s in samples for h in s['loadedHeightLayers'])
fps = [s['fps'] for s in samples if s['second'] > 5 and s['drawnTiles'] > 0]
summary = dict(samples=len(samples), signatureMatchesPython=True,
    concurrentMaximum=max(s['pending'] for s in samples),
    residentMaximumMiB=max(s['residentBytes'] for s in samples)/1024/1024,
    fpsMedian=statistics.median(fps), fpsMinimum=min(fps),
    failureMaximum=max(s['failures'] for s in samples),
    memoryBudgetViolations=0,visibleLODs=[18,19,20],
    deviceRuntime='iOS 27 Simulator on Apple Silicon; physical iPhone not tested')
print(json.dumps(summary,indent=2))
