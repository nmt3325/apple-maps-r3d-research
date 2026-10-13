#!/usr/bin/env python3
"""Native-free C3MM v2 section parser. Only local captured samples."""
import struct,lzma,json,sys
from pathlib import Path
def parse(b, include_cells=False):
 if len(b)<12 or b[:6]!=b'C3MM\x02\x00':raise ValueError('Header')
 sub,count=struct.unpack_from('<HI',b,6)
 if sub!=3 or count not in (6,7):raise ValueError('Section table')
 pos=12;sections=[];raw_sections={}
 for i in range(count):
  if len(b)-pos<5:raise ValueError('Truncated record')
  tag=b[pos];size=struct.unpack_from('<I',b,pos+1)[0]
  if size<5 or size>len(b)-pos:raise ValueError('Invalid record bounds')
  end=pos+size
  if tag==4:
   if size!=15:raise ValueError('Unknown inline record')
   payload=b[pos+5:end];codec='inline'
  else:
   if size<23 or b[pos+5]!=1:raise ValueError('Unknown compression method')
   expected=struct.unpack_from('<I',b,pos+6)[0]
   if expected>100000000:raise ValueError('Too large')
   stream=b[pos+10:end]
   if stream[:5]!=bytes.fromhex('5d00001000'):raise ValueError('Unknown LZMA format')
   payload=lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(stream,max_length=expected)
   if len(payload)!=expected:raise ValueError('Wrong decompressed size')
   codec='LZMA'
  item={'tag':tag,'offset':pos,'size':size,'codec':codec,'uncompressed':len(payload)}
  if tag==1:
   number=struct.unpack_from('<I',payload)[0]
   item['count16']=number
   item['count16Matches']=len(payload)==4+number*2
  raw_sections[tag]=payload
  sections.append(item);pos=end
 if pos!=len(b):raise ValueError('Unexpected trailing data')
 if [x['tag'] for x in sections] not in ([0,8,9,1,5,6],[4,0,8,9,1,5,6]):
  raise ValueError('Unexpected section order')
 n,=struct.unpack_from('<H',raw_sections[8],0)
 if len(raw_sections[8])!=2+8*n:raise ValueError('Tag 8 record table mismatch')
 if struct.unpack_from('<H',raw_sections[9])[0]!=n or len(raw_sections[9])!=2+4*n:
  raise ValueError('Tag 9 record table mismatch')
 if len(raw_sections[0])!=12+4*n:raise ValueError('Tag 0 record table mismatch')
 if len(raw_sections[5])!=9+4*n:raise ValueError('Tag 5 record table mismatch')
 m=struct.unpack_from('<I',raw_sections[1])[0]
 if len(raw_sections[6])!=1+2*(m-n):raise ValueError('Tag 6 count mismatch')
 for item in sections:
  if item['tag'] in (0,8,9,5):item['sharedRecordCount']=n
  if item['tag'] in (8,9):
   width=8 if item['tag']==8 else 4
   fmt='<Q' if width==8 else '<I'
   vals=[v[0] for v in struct.iter_unpack(fmt,raw_sections[item['tag']][2:])]
   item['uniqueValues']=len(set(vals))
   item['valueMin']=min(vals)
   item['valueMax']=max(vals)
  if item['tag']==0:
   values=[v[0] for v in struct.iter_unpack('<I',raw_sections[0][12:])]
   item['firstTwelveBytes']=raw_sections[0][:12].hex()
   header=raw_sections[0]
   zoom_hi=header[0]
   south_index=struct.unpack_from('<I',header,1)[0]
   east_index=struct.unpack_from('<I',header,5)[0]
   zoom_lo=header[9]
   count16=struct.unpack_from('<H',header,10)[0]
   if not (zoom_hi>=4 and zoom_hi<=30 and zoom_lo==zoom_hi+3 and
           east_index%16==0 and south_index%16==0 and count16==n):
    raise ValueError('Invalid coordinate index header')
   xx=east_index//16
   yy=((1<<zoom_hi)-south_index)//16-1
   zz=zoom_hi-4
   if not (0<=xx<1<<zz and 0<=yy<1<<zz):raise ValueError('Tile position out of range')
   item['decodedTile']={'z':zz,'x':xx,'y':yy}
   item['firstIndexValues']=values[:16]
   item['u32Unique']=len(set(values))
   item['u32Range']=[min(values),max(values)]
   item['packedBitmask']=hex(__import__('functools').reduce(lambda a,b:a|b,values,0))
   item['lowByteValues']=sorted(set(x&255 for x in values))
   item['distinctXY']=len(set(((x>>8)&15,(x>>20)&15) for x in values))
   item['unaccountedBits']=hex(__import__('functools').reduce(lambda a,b:a|b,values,0)&~0x00f00fff)
  if item['tag']==5:
   item['floatPairCandidate']=list(struct.unpack_from('<2f',raw_sections[5],0))
   item['quantizerBitsCandidate']=raw_sections[5][8]
   pairs=list(struct.iter_unpack('<HH',raw_sections[5][9:]))
   item['orderedAltitudePairCount']=sum(a<=b for a,b in pairs)
   item['pairCount']=len(pairs)
   item['maxQuantizedBound']=max(max(a,b) for a,b in pairs)
   values=[v[0] for v in struct.iter_unpack('<I',raw_sections[5][9:])]
   item['u32Unique']=len(set(values))
   item['u32Range']=[min(values),max(values)]
 if include_cells:
  indexes=[v[0] for v in struct.iter_unpack('<I',raw_sections[0][12:])]
  cells={(v>>8&15,v>>20&15,v&255) for v in indexes}
  if len(cells)!=n:raise ValueError('Duplicate indexed tile')
  return sections,cells
 return sections
if __name__=='__main__':
 for name in sys.argv[1:]:
  row=parse(Path(name).read_bytes())
  print(Path(name).name,json.dumps(row))
