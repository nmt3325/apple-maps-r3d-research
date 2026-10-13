#!/usr/bin/env python3
"""Static call graph of native r3d_world_read_mem from the iOS27 VectorKit binary."""
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from collections import Counter,defaultdict
import subprocess,bisect
p=Path(__file__).parent/'Extracted'/'VectorKit'
raw=p.read_bytes()
syms=[]
for line in subprocess.run(['nm','-an',str(p)],capture_output=True,text=True).stdout.splitlines():
 try:
  addr=int(line.split(' ',1)[0],16); typ=line.split()[1]; name=line.split(maxsplit=2)[2]
  if typ.lower() in ('t','w','s'):syms.append((addr,name))
 except Exception:pass
syms.sort();addrs=[s[0] for s in syms]
def lookup(addr):
 k=bisect.bisect_right(addrs,addr)-1
 if k<0:return 'unknown'
 old,n=syms[k]
 return (n[:110] if addr==old else f'{n[:90]}+{addr-old:x}')
start=0x1b70a1914;end=0x1b70ade60;base=0x1b5ebc000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
calls=Counter();samples=defaultdict(list)
for ins in md.disasm(raw[start-base:end-base],start):
 if ins.mnemonic not in ('bl','blr'):continue
 if ins.mnemonic=='bl':
  try:t=int(ins.op_str.lstrip('#'),16);name=lookup(t) if start<=t<end else lookup(t)
  except Exception:name=ins.op_str
 else:name='indirect '+ins.op_str
 calls[name]+=1
 if len(samples[name])<7:samples[name].append(hex(ins.address))
print('r3d_world_read_mem instructions',len(raw[start-base:end-base])//4)
for n,c in calls.most_common(90):print(str(c).rjust(3),n,'at',','.join(samples[n]))
