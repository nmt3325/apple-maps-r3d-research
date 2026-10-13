from pathlib import Path
import lzma
base=Path('/root/.desktop-mcp/linux-4ebec5ed/work/apple-maps-region-fetch-lab-20261013/exports')
items=[(base/'tower-missing-check/s100_z9_x454_y201_h0.c3mm',37,287,1024),(base/'capture-validation-b/s100_z13_x7276_y3225_h0.c3mm',22,319,1040)]
for f,start,length,expected in items:
 blob=f.read_bytes();payload=blob[start:start+length]
 d=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
 try:
  out=d.decompress(payload,max_length=expected)
  print(f.name,'target',expected,'actual',len(out),'needs_input',d.needs_input,'eof',d.eof,'head',out[:32].hex())
 except Exception as e:print(f.name,type(e).__name__,str(e))
