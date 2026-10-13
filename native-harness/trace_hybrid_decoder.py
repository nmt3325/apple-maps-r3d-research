from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import subprocess,bisect,collections
p=Path('/Users/denken/.desktop-mcp/mac-6dd4602a/work/ios27-vectorkit-analysis/Extracted/VectorKit')
raw=p.read_bytes();base=0x1b5ebc000
start=0x1b6cf3334;end=0x1b6cf859c
syms=[]
for line in subprocess.check_output(['nm','-an',str(p)],text=True).splitlines():
 fields=line.split(maxsplit=2)
 if len(fields)!=3:continue
 try:
  if fields[1].lower() in ('t','w'):syms.append((int(fields[0],16),fields[2]))
 except ValueError:pass
syms.sort();addrs=[a for a,n in syms]
def lookup(a):
 i=bisect.bisect_right(addrs,a)-1
 if i<0:return '?'
 x,n=syms[i]
 return n[:125]+('+'+hex(a-x) if a!=x else '')
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
calls=[]
for ins in md.disasm(raw[start-base:end-base],start):
 if ins.mnemonic=='bl':
  a=int(ins.op_str.replace('#',''),16)
  calls.append((ins.address,a,lookup(a)))
print('R3dResourceDecoder::decode callsites',len(calls),'unique targets',len(set(x[1] for x in calls)))
for addr,target,name in calls:
 if 'create' in name.lower() or 'r3d' in name.lower() or 'model' in name.lower() or 'splats' in name.lower() or 0x1b70a0000<=target<=0x1b70b5000:
  print(hex(addr),'=>',hex(target),name)
