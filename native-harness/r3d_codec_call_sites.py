from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
b=Path('/Users/denken/.desktop-mcp/mac-6dd4602a/work/ios27-vectorkit-analysis/Extracted/VectorKit').read_bytes()
base=0x1b5ebc000
start=0x1b70a1914;end=0x1b70ade60
ins=list(Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(b[start-base:end-base],start))
targets={0x1b7097500:'mesh',0x1b709c238:'soup',0x1b709decc:'byet',0x1b70b0040:'field_next'}
for ix,i in enumerate(ins):
 if i.mnemonic=='bl':
  try:d=int(i.op_str.lstrip("#"),16)
  except:continue
  if d in targets and (d!=0x1b70b0040):
   print('\n*******',targets[d],'CALLER',hex(i.address),'*******')
   for a in ins[max(0,ix-25):ix+11]:print(hex(a.address),a.mnemonic,a.op_str)
