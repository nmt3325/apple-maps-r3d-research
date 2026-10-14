import sys,struct,json
from pathlib import Path
sys.path.insert(0,'/opt/flyover-viewer')
sys.path.insert(0,'/opt/flyover-viewer/nativefree-lab-20261013')
from nativefree_r3d_codec_streams import dissect
from nativefree_byet_jdescriptor import split_j
from nativefree_trico_size import read_size
from nativefree_huff816 import parse_table
p=sorted(Path('/opt/flyover-viewer/native-r3d').glob('*.r3d'))[0];raw=p.read_bytes();s=dissect(raw)['splatStream'];print('file',p.name,'n',s['pointCount'])
for f in s['blocks']:
 q=f['byet'];j=raw[s['offset']+q['compressedPayloadRelativeOffset']:s['offset']+q['compressedPayloadRelativeOffset']+q['compressedPayloadBytes']];spec=split_j(j,12 if f['index']==0 else 32)
 for d in spec['descriptors']:
  lane=j[d['compressedOffset']:d['compressedOffset']+d['compressedBytes']]
  if lane[4:8]!=bytes.fromhex('00000024'):continue
  size0,count0=struct.unpack_from('<IQ',lane,8)
  tab,at,stats=parse_table(lane[24:],8)
  vals=[]
  for pos in (0,1,2,4,8,12,16,20,24):
   try:
    n,q=read_size(lane,pos);vals.append([pos,n,q])
   except (ValueError,IndexError):pass
  print(json.dumps(dict(block=f['index'],kind=d['kind'],lane=d['lane'],laneBytes=len(lane),hexFirst48=lane[:48].hex(),huffSize0=size0,huffCount0=count0,tableBytes=at,tableBits=stats['tableBits'],huffSymbolTypes=len(tab),compactedReadSize=vals)))
