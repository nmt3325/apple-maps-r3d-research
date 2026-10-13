#!/usr/bin/env python3
from pathlib import Path
import json
def varint(b,p,end):
 v=0
 for k in range(10):
  if p>=end:raise ValueError('truncated')
  c=b[p];p+=1
  if k==9 and c>1:raise ValueError('overflow')
  v|=(c&0x7f)<<(7*k)
  if not c&0x80:return v,p
 raise ValueError('long uleb')
def parse(b,lo,hi):
 p=lo;result=[]
 while p<hi:
  key,p=varint(b,p,hi);n,p=varint(b,p,hi)
  if n>hi-p:raise ValueError('length out of bounds')
  result.append((key,p,n));p+=n
 return result
def possible(b,lo,hi):
 for skip in (0,1,2,3,4):
  if hi-lo<8:break
  try:
   out=parse(b,lo+skip,hi)
   if 2<=len(out)<=80 and max(x[0] for x in out)<=24:
    return skip,out
  except:pass
 return None
def tree(b,lo,hi,depth=0):
 if depth>=6:return []
 result=[]
 pars=possible(b,lo,hi)
 if pars is None:return result
 skip,fields=pars
 for kind,off,n in fields:
  node={'tag':kind,'offset':off,'bytes':n}
  subtree=tree(b,off,off+n,depth+1) if n>32 else []
  if subtree:node['children']=subtree
  result.append(node)
 return result
if __name__=='__main__':
 import sys
 p=Path(sys.argv[1]);b=p.read_bytes()
 fields=parse(b,11,len(b))
 print(json.dumps({'file':p.name,'bytes':len(b),
  'major':[{'tag':x,'offset':y,'bytes':z,'children':tree(b,y,y+z)} for x,y,z in fields]},
  ensure_ascii=False,indent=2))
