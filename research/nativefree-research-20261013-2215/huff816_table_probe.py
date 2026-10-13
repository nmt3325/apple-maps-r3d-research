#!/usr/bin/env python3
"""Experimental Huff816 codebook parser; does not decode payload symbols."""
import struct
class HuffError(ValueError):pass
class Bits:
 def __init__(self,src):
  self.src=src
  self.at=0
 def take(self,n):
  if n<0 or n>32 or self.at+n>len(self.src)*8:raise HuffError('truncated bits')
  v=0
  for i in range(n):
   at=self.at+i
   byte=self.src[(at//32)*4+(3-(at%32)//8)]
   v=(v<<1)|((byte>>(7-at%8))&1)
  self.at+=n
  return v

def table(stream:bytes,width=8):
 if len(stream)<8:raise HuffError('short Huff816')
 h=struct.unpack_from('<I',stream)[0]
 if h!=0x61000002:raise HuffError(f'unsupported header {h:#x}')
 b=Bits(stream[4:])
 count=b.take(width)+1
 width_codes=b.take(3)
 sym=0
 entries=[]
 for i in range(count):
  if width_codes==0:
   n=1 if count==2 else 0
   code=b.take(1) if n else 0
  else:
   n=b.take(width_codes)+1
   code=b.take(n)
  if b.take(1):
   if b.take(1):sym=b.take(width)
   else:sym+=b.take(width//2)
  entries.append((n,code,sym))
  sym+=1
 return {'entries':entries,'count':count,'codeWidth':width_codes,'bitOffset':b.at,
         'symbolValid':all(0<=x[2]<1<<width for x in entries),
         'uniqueSymbols':len(set(x[2] for x in entries))==len(entries),
         'uniqueCodes':len(set((x[0],x[1]) for x in entries))==len(entries),
         'kraft':sum(2**(-x[0]) for x in entries)}

if __name__=='__main__':
 import sys
 raw=bytes.fromhex(sys.argv[1])
 print(table(raw))
