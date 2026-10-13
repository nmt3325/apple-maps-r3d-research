#!/usr/bin/env python3
"""Read iOS27 VectorKit Mach-O load commands, decode ADRP+ADD PC-relative references to cstrings."""
import struct, pathlib, sys, collections
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM, arm64
LIB=pathlib.Path(__file__).parent/'Extracted'/'VectorKit'
data=LIB.read_bytes()
magic,cputype,subtype,filetype,ncmds,sizeofcmds,flags,reserved=struct.unpack_from('<8I',data,0)
assert magic==0xfeedfacf
segs=[];sections=[];off=32
for c in range(ncmds):
 cmd,size=struct.unpack_from('<II',data,off)
 if cmd==0x19:
  segname,vm,vm_size,fo,fs,ma,ia,ns,fl=struct.unpack_from('<16sQQQQIIII',data,off+8)
  name=segname.split(bytes([0]),1)[0].decode('ascii','replace')
  segs.append((name,vm,vm_size,fo,fs))
  for j in range(ns):
   ss=off+72+j*80
   sect,ssname,addr,slen,soff=struct.unpack_from('<16s16sQQI',data,ss)
   sections.append((sect.split(bytes([0]),1)[0].decode('ascii','replace'),ssname.split(bytes([0]),1)[0].decode('ascii','replace'),addr,slen,soff))
 off+=size
print('VM segments')
for x in segs:print(x[0],hex(x[1]),hex(x[2]),hex(x[3]),hex(x[4]))
print('SECTIONS SAMPLE',sections[:6]);print('Relevant sections')
for x in sections:
 if any(q in x[0] for q in ('text','cstring','const','oslog')): print(x[0],x[1],hex(x[2]),hex(x[3]),hex(x[4]))
for phrase in [b'Failed to decompress mesh chunk',b'C3m - Invalid header type',b'FlyoverSplatsShader',b'SPUTNIK_C3M']:
 start=0;found=[]
 while True:
  f=data.find(phrase,start)
  if f<0:break
  s=next((k for k in sections if k[4]<=f<k[4]+k[3]),None)
  va=(s[2]+f-s[4]) if s else None
  found.append((hex(f),hex(va) if va else '?',s[0] if s else '-'))
  start=f+len(phrase)
  if len(found)>10:break
 print('STRING',phrase.decode(),found)
