from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
import subprocess,collections,bisect
p=Path('/Users/denken/.desktop-mcp/mac-6dd4602a/work/ios27-vectorkit-analysis/Extracted/VectorKit')
bin=p.read_bytes();base=0x1b5ebc000;st=0x1b70a1914;en=0x1b70ade60
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
labels=[]
for line in subprocess.check_output(['nm','-an',str(p)],text=True).splitlines():
 a=line.split(maxsplit=2)
 if len(a)!=3:continue
 try:
  if a[1] in ('t','T','W'):labels.append((int(a[0],16),a[2]))
 except:pass
labels.sort();addrs=[a for a,n in labels]
def near(v):
 k=bisect.bisect_right(addrs,v)-1
 if k<0:return '?'
 a,n=labels[k];return n[:75]+('+'+hex(v-a) if v>a else '')
stats=collections.Counter()
allcalls=[]
for i in md.disasm(bin[st-base:en-base],st):
 if i.mnemonic not in ('bl','blr'):continue
 try:to=int(i.op_str.lstrip('#'),16)
 except:continue
 stats[(to,near(to))]+=1;allcalls.append((i.address,to))
print('instructions',len(bin[st-base:en-base])//4,'calls',len(allcalls),'unique',len(stats))
for (to,name),n in stats.most_common(65):print(hex(to),n,name)
