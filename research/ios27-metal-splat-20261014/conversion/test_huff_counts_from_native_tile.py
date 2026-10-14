from pathlib import Path
import sys,json,collections,struct
sys.path.insert(0,'/opt/flyover-viewer')
sys.path.insert(0,'/opt/flyover-viewer/nativefree-lab-20261013')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from analyze_lane_framing_v2 import classify
from huff816_envelope import split_envelope
from nativefree_huff816 import decode_symbols,Huff816Error
p=sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))[0];raw=p.read_bytes();s=dissect(raw)['splatStream'];n=s['pointCount'];reports=[]
for f in s['blocks']:
 q=f['byet'];j=raw[s['offset']+q['compressedPayloadRelativeOffset']:s['offset']+q['compressedPayloadRelativeOffset']+q['compressedPayloadBytes']];spec=split_j(j,12 if f['index']==0 else 32)
 for d in spec['descriptors']:
  if not d['compressedBytes']:continue
  lane=j[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']];kind=classify(lane)
  if kind=='wrapper24_at4':segments=split_envelope(lane,4);streams=[lane[x.offset:x.offset+x.compressed_size] for x in segments]
  elif kind.startswith('direct_huff_at'):streams=[lane[int(kind.split('at')[1]):]]
  else:continue
  for h in streams[:3]:
   if len(h)<4 or h[3]&128:continue
   tests=[]
   for count in (n,3*n):
    try:
     result,stats=decode_symbols(h,8,count)
     tests.append(dict(count=count,success=True,entropyBitsConsumed=stats.get('entropyBitsConsumed'),totalEntropyPayloadBytes=len(h)-4-stats.get('alignedBytes',0)))
    except (ValueError,OverflowError) as exc:tests.append(dict(count=count,success=False,error=str(exc)[:90]))
   reports.append(dict(block=f['index'],kind=d['kind'],lane=d['lane'],family=kind,huffBytes=len(h),tests=tests))
print(json.dumps(dict(tile=p.name,n=n,results=reports[:35]),indent=2))
