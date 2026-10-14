"""Check every vertical candidate response and preservation of upper-layer geometry."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import numpy as np


def audit(run_dir, baseline=None):
    run=json.loads((run_dir/'run.json').read_text())
    fetch=json.loads((run_dir/'raw/fetch.json').read_text())
    decoded=json.loads((run_dir/'decoded/manifest.json').read_text())
    scene=json.loads((run_dir/'viewer/scene.json').read_text())
    assert run['pass'] and not run['nativeGoldenInput']
    key=lambda t:(t['z'],t['x'],t['y'],t['h'])
    planned=[key(t) for t in fetch['plan']['tiles']]
    returned=[key(f['tile']) for f in fetch['files']]
    empty=[key(f['tile']) for f in fetch['emptyTiles']]
    assert len(planned)==len(set(planned)) and Counter(planned)==Counter(returned+empty)
    assert not fetch['errors']
    sources={f['file']:f for f in fetch['files']}
    assert sources.keys()=={t['source'] for t in decoded['results']}=={t['source'] for t in scene['tiles']}
    for name,f in sources.items():
        assert hashlib.sha256((run_dir/'raw'/name).read_bytes()).hexdigest()==f['sha256']
    layers={};height_ranges={'mesh':[],'visibleSplat':[]}
    for tile in scene['tiles']:
        h=int(re.search(r'_h(\d+)\.r3d$',tile['source'])[1])
        layer=layers.setdefault(h,{'tiles':0,'meshTriangles':0,'splatRecords':0,'visibleSplatRecords':0,'meshHeight':[],'visibleSplatHeight':[]})
        for key_name in ('tiles','meshTriangles','splatRecords','visibleSplatRecords'):
            layer[key_name]+=1 if key_name=='tiles' else tile['triangles'] if key_name=='meshTriangles' else tile[key_name]
        data=(run_dir/'viewer'/tile['mesh']).read_bytes();n=int(np.frombuffer(data,'<u4',4)[2])
        mesh=np.frombuffer(data,'<f4',3*n,16).reshape(-1,3)
        data=(run_dir/'viewer'/tile['splats']).read_bytes();n=int(np.frombuffer(data,'<u4',4)[2])
        splat=np.frombuffer(data,'<f4',9*n,16).reshape(n,3,3)
        rgba=np.frombuffer(data,'u1',4*n,16+36*n).reshape(n,4)
        visible=splat[rgba[:,3]>0].reshape(-1,3)
        assert np.isfinite(mesh).all() and np.isfinite(splat).all()
        for values,label,global_label in ((mesh,'meshHeight','mesh'),(visible,'visibleSplatHeight','visibleSplat')):
            if len(values):
                pair=[float(values[:,1].min()),float(values[:,1].max())]
                layer[label].append(pair);height_ranges[global_label].append(pair)
    for layer in layers.values():
        for label in ('meshHeight','visibleSplatHeight'):
            pairs=layer[label];layer[label]=[min(p[0] for p in pairs),max(p[1] for p in pairs)] if pairs else None
    preserved=0
    if baseline:
        old=json.loads((baseline/'manifest.json').read_text())
        new={t['source']:t for t in decoded['results']}
        for tile in old['results']:
            assert new[tile['source']]['sourceSHA256']==tile['sourceSHA256']
            assert new[tile['source']]['arrays']==tile['arrays']
            preserved+=len(tile['arrays'])
    return {'pass':True,'nativeGoldenInput':False,'candidateRequests':len(planned),'nonemptyTiles':len(returned),
            'emptyResponses':len(empty),'everyCandidateAccountedFor':True,'allOriginalHashesMatch':True,
            'baselineArraysAndImagesPreserved':preserved,'layers':layers,'totals':scene['totals'],
            'heightRangesMeters':{k:[min(p[0] for p in v),max(p[1] for p in v)] for k,v in height_ranges.items()}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    p.add_argument('--baseline',type=Path);p.add_argument('--report',type=Path,required=True)
    args=p.parse_args();report=audit(args.run,args.baseline)
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
