#!/usr/bin/env python3
"""C3MM v2 six-LZMA-block read-only sample audit.
This is an envelope reader, not a tile-index or octree semantic decoder.
"""
from pathlib import Path
import lzma,struct,json,hashlib,collections
DATA=Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013')
OUT=Path(__file__).parent/'c3mm-v2-sequential-report.json'
MAGIC=b'\x5d\x00\x00\x10\x00'
rows=[]
for f in sorted(DATA.rglob('*.c3mm')):
 b=f.read_bytes()
 assert b[:6]==b'C3MM\x02\x00',(f,'wrong header')
 pos=b.find(MAGIC)
 assert pos>=9
 start=pos-9
 report={'source':str(f.relative_to(DATA)),'fileBytes':len(b),
         'prologue':b[:start].hex(),'prologueBytes':start,'records':[]}
 at=start
 for i in range(6):
  assert b[at+9:at+14]==MAGIC,(f,i,'not sequential')
  total=struct.unpack_from('<I',b,at)[0]
  mode=b[at+4]
  rawlen=struct.unpack_from('<I',b,at+5)[0]
  assert mode==1 and total>=22 and rawlen<1_000_000
  end=at+total
  assert end<=len(b)+1
  dec=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
  payload=dec.decompress(b[at+9:min(end,len(b))],max_length=rawlen)
  assert len(payload)==rawlen,(f,i,rawlen,len(payload))
  n=len(payload);c=collections.Counter(payload)
  report['records'].append({
    'ordinal':i,'sectionTag':b[at-1],'recordStart':at,'encodedBytes':total,
    'decodedBytes':n,'prefix32':payload[:32].hex(),
    'sha256':hashlib.sha256(payload).hexdigest(),
    'distinctBytes':len(c),
    'candidateUint16Array': (n>=4 and i==3 and 2*struct.unpack_from('<I',payload,0)[0]+4==n),
    'firstTwoFloat32': list(struct.unpack_from('<2f',payload,0)) if i==4 else None,
    'zeroPercent':round(100*c[0]/n,1),
    'terminalInputShortBy':max(0,end-len(b)),
    'recordEnd':end
  })
  at=end
 assert at-len(b) in (0,1),(f,'envelope mismatch',at,len(b))
 rows.append(report)
out={'files':len(rows),'validBlocks':sum(len(x['records']) for x in rows),'allSixValid':all(len(x['records'])==6 for x in rows),'rows':rows}
OUT.write_text(json.dumps(out,indent=2))
for r in rows:
 print(r['source'], 'prologue',r['prologue'], 'ending gap',r['records'][-1]['terminalInputShortBy'])
 for t in r['records']:
  print('  ',t['ordinal'],'tag',t['sectionTag'],'encoded',t['encodedBytes'],'decoded',t['decodedBytes'],'zeros',t['zeroPercent'],'prefix',t['prefix32'])
print('PASS',out['validBlocks'],'records; saved',OUT)
