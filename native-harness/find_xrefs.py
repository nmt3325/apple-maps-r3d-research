#!/usr/bin/env python3
"""Find real ARM64 ADRP+ADD cross-references to Flyover splat parsing strings in extracted iOS27 VectorKit."""
from pathlib import Path
import struct
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
d=Path(__file__).parent/'Extracted'/'VectorKit'
b=d.read_bytes()
text_start=0x1920; text_len=0x121b2d0; text_va=0x1b5ebd920
targets=[
'Failed to decompress mesh chunk',
'C3m - Invalid header type',
'C3m invalid block type',
'C3m Block size too large',
'Failed to read C3m file',
'SPUTNIK_C3M',
'FlyoverSplatsShader',
'Failed to read C3mm file',
'Unsupported C3MM version',
]
found={}
for t in targets:
 pos=b.find(t.encode())
 if pos<0:continue
 assert pos<0x1400000
 va=0x1b5ebc000+pos
 found[t]=(va,pos)
print('STRINGS',{k:hex(v[0]) for k,v in found.items()},flush=True)
target_pages={addr&~0xfff for addr,_ in found.values()}
data=memoryview(b)[text_start:text_start+text_len]
masks=(0x90000000,0x9f000000)
found_refs={}
for i in range(0,len(data)-4,4):
 inst=struct.unpack_from('<I',data,i)[0]
 if inst&0x9f000000 !=0x90000000:continue
 pc=text_va+i
 immhi=(inst>>5)&0x7ffff;immlo=(inst>>29)&3
 imm=(immhi<<2)|immlo
 if imm & (1<<20):imm-=1<<21
 page=(pc&~0xfff)+(imm<<12)
 if page not in target_pages:continue
 rd=inst&31
 for delta in range(1,8):
  if i+delta*4+4>len(data):break
  op=struct.unpack_from('<I',data,i+delta*4)[0]
  if op&0xff000000!=0x91000000:continue
  rn=(op>>5)&31
  if rn!=rd:continue
  imm12=(op>>10)&0xfff;shift=(op>>22)&3
  if shift>1:continue
  addr=page+(imm12<< (12 if shift else 0))
  for name,(target,off) in found.items():
   if target==addr:
    found_refs.setdefault(name,[]).append((pc,i,delta,rd))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
for name,refs in found_refs.items():
 print('\nNAME',name,'refs',len(refs),flush=True)
 for pc,i,delta,rd in refs[:15]:
  print('XREF',hex(pc),'file',hex(i+text_start),'target',hex(found[name][0]))
  ix=max(0,i-32)
  for ins in md.disasm(bytes(data[ix:i+72]),text_va+ix):
   print(' ',hex(ins.address),ins.mnemonic,ins.op_str)
