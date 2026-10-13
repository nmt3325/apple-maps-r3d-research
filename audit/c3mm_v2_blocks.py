#!/usr/bin/env python3
"""Inspect C3MM-v2 LZMA blocks with externally declared size and length.
Input is previously captured local files. Never reads network or access tokens.
"""
from pathlib import Path
import hashlib,json,lzma,struct
BASE=Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013')
OUT=Path(__file__).parent/'c3mm-v2-block-report.json'
MAGIC=bytes.fromhex('5d00001000')
reports=[]
for f in sorted(BASE.rglob('*.c3mm')):
 b=f.read_bytes();blocks=[];at=0
 while True:
  offset=b.find(MAGIC,at)
  if offset<0:break
  at=offset+1
  if offset<9:continue
  begin=offset-9
  total=struct.unpack_from('<I',b,begin)[0]
  mode=b[begin+4]
  rawlen=struct.unpack_from('<I',b,begin+5)[0]
  end=begin+total
  if not(9<total and end<=len(b)+1 and rawlen<=80000000):continue
  item={'offset':offset,'recordOffset':begin,'recordBytes':total,'method':mode,'declaredRawBytes':rawlen,'missingTrailingBytes':max(0,end-len(b))}
  try:
   stream=b[offset:end]
   dec=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
   data=dec.decompress(stream,max_length=rawlen)
   item.update(decodedBytes=len(data),sizeMatches=len(data)==rawlen,sha256=hashlib.sha256(data).hexdigest(),prefix=data[:16].hex(),eof=dec.eof)
  except lzma.LZMAError as e:item['failure']=str(e)
  blocks.append(item)
 reports.append({'file':str(f.relative_to(BASE)),'fileBytes':len(b),'blocks':blocks})
report={'files':len(reports),'recognizedBlocks':sum(len(r['blocks']) for r in reports),'successfulBlocks':sum(x.get('sizeMatches',False) for r in reports for x in r['blocks']),'samples':reports}
OUT.write_text(json.dumps(report,indent=2))
print('source files',report['files'],'blocks',report['recognizedBlocks'],'valid',report['successfulBlocks'])
for r in reports:
 print(r['file'],'blocks',len(r['blocks']), 'status',[(x['recordBytes'],x['declaredRawBytes'],x.get('decodedBytes'),x.get('failure')) for x in r['blocks'][:12]])
print('Wrote',OUT)
