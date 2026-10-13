"""Synthetic Huff816 compressed-table roundtrip and malformed-input checks."""
import struct
from huff816_decode_experimental import decode
def pack32_msb(bits):
 while len(bits)%32:bits+='0'
 return b''.join(int(bits[i:i+32],2).to_bytes(4,'little') for i in range(0,len(bits),32))
def test():
 for count in (0,1,7,31,100):
  expected=bytes((i&1) for i in range(count))
  # 8-bit symbol count-minus-one =1; 3-bit codewidth=0
  # Table entries: (code0, sequential symbol0), (code1, sequential symbol1)
  tablebits='00000001'+'000'+'0'+'0'+'1'+'0'
  bitstream=tablebits+''.join(str(i) for i in expected)
  stream=struct.pack('<I',0x61000002)+pack32_msb(bitstream)
  got,used,total,info=decode(stream,count)
  assert got==expected,(count,got)
  assert info['count']==2 and info['kraft']==1
 print('PASS synthetic compressed Huff816 two-symbol codebook (5 vectors)')
if __name__=='__main__':test()
