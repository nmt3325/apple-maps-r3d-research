"""Independent experimental Huff816 entropy decoder for Apple R3D lane payloads."""
from huff816_table_probe import table,Bits,HuffError
class NeedMoreBits(HuffError):pass

def decode(stream:bytes,count:int,width:int=8):
 if count<0 or count>10_000_000:raise ValueError('unsafe output count')
 info=table(stream,width)
 entries=info['entries']
 lookup={}
 for n,code,sym in entries:
  if n<=0 or n>20:raise HuffError('unsupported code length')
  lookup[(n,code)]=sym
 for n,code,sym in entries:
  for p in range(1,n):
   if (p,code>>(n-p)) in lookup:raise HuffError('prefix collision')
 reader=Bits(stream[4:])
 reader.at=info['bitOffset']
 reader.src=reader.src[:len(reader.src)//4*4]
 out=bytearray()
 max_len=max(x[0] for x in entries)
 for _ in range(count):
  c=0
  for n in range(1,max_len+1):
   try:c=(c<<1)|reader.take(1)
   except HuffError as e:raise NeedMoreBits(str(e))
   if (n,c) in lookup:
    out.append(lookup[(n,c)])
    break
  else:raise HuffError('invalid Huffman code')
 return bytes(out),reader.at,len(reader.src)*8,info
