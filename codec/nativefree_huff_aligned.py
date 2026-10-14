#!/usr/bin/env python3
"""Independent Huff816 table parser (Apple R3D interoperability research).

Reads bits MSB-first inside each *little-endian* 32-bit word, as indicated
by the ARM64 decoder's LDR W + LSL #32 bit reservoir. Does not call VectorKit.
The table is followed by a 32-bit-word-aligned entropy payload.

Only expose decoded symbols after prefix-code validation; never fabricate
data for unsupported variants.
"""
from dataclasses import dataclass
from collections import Counter
import struct

class Huff816Error(ValueError): pass

class WordBits:
    def __init__(self, data: bytes, pos: int=0):
        self.data=data
        self.pos=pos
    def read(self,n):
        if not 0<=n<=32: raise Huff816Error('invalid bit width')
        if self.pos+n>len(self.data)*8: raise Huff816Error('truncated word-bit stream')
        out=0
        remaining=n
        while remaining:
            word=self.pos//32
            offset=self.pos%32
            start=word*4
            if start+4>len(self.data):raise Huff816Error('partial uint32 word')
            value=struct.unpack_from('<I',self.data,start)[0]
            take=min(remaining,32-offset)
            out=(out<<take)|((value>>(32-offset-take))&((1<<take)-1))
            self.pos+=take
            remaining-=take
        return out
    def align_word(self):
        self.pos=(self.pos+31)&~31

@dataclass(frozen=True)
class Entry:
    code:int
    bits:int
    symbol:int

def parse_table(data:bytes,width:int):
    if width not in (8,16):raise Huff816Error('width must be 8 or 16')
    r=WordBits(data)
    n=r.read(width)+1
    if n>1<<width:raise Huff816Error('invalid symbol count')
    len_width=r.read(3)
    symbols=[]
    symbol=0
    for i in range(n):
        if len_width:
            bits=r.read(len_width)+1
            code=r.read(bits)
        else:
            bits=1 if n==2 else 0
            code=r.read(1) if n==2 else 0
        if r.read(1):
            if r.read(1):
                symbol=r.read(width)
            else:
                symbol+=r.read(width//2)
        symbols.append(Entry(code,bits,symbol))
        symbol+=1
        if symbol>1<<width and i!=n-1:
            raise Huff816Error('symbol range exceeds word width')
    consumed=r.pos
    r.align_word()
    if r.pos>len(data)*8:raise Huff816Error('table alignment exceeds input')
    return symbols,r.pos//8,dict(symbols=n,codeLengthWidth=len_width,
                              tableBits=consumed,alignedBytes=r.pos//8,
                              lengths=dict(Counter(x.bits for x in symbols)))

def build_tree(entries):
    root={}
    for entry in entries:
        if entry.bits==0:
            if len(entries)!=1:raise Huff816Error('zero-length code with multiple symbols')
            return {'constant':entry.symbol}
        node=root
        for shift in range(entry.bits-1,-1,-1):
            if 'symbol' in node:raise Huff816Error('prefix conflict')
            bit=(entry.code>>shift)&1
            node=node.setdefault(bit,{})
        if node:raise Huff816Error('duplicate code or prefix conflict')
        node['symbol']=entry.symbol
    return root

def decode_symbols(data:bytes,width:int,count:int):
    if count<0 or count>20000000:raise Huff816Error('unreasonable output count')
    if len(data)<4:raise Huff816Error('truncated Huff816 header')
    hdr=struct.unpack_from('<I',data)[0]
    if (hdr&0x7f0000ff)!=0x61000002:
        raise Huff816Error(f'unsupported Huff816 marker {hdr:08x}')
    if hdr&0x80000000:
        if len(data)!=4+count*(width//8):
            raise Huff816Error('literal length differs from requested output')
        return data[4:],{'mode':'literal','count':count}
    entries,at,stats=parse_table(data[4:],width)
    tree=build_tree(entries)
    if 'constant' in tree:
        vals=[tree['constant']]*count
        consumed=0
    else:
        bits=WordBits(data[4+at:])
        # A bounded prefix table handles common codes with one word read.
        # Longer codes continue through the validated tree; the final word
        # uses the tree directly when there are fewer lookahead bits left.
        lookahead=min(10,max(entry.bits for entry in entries))
        lookup=[]
        for prefix in range(1<<lookahead):
            node=tree
            used=0
            while used<lookahead and 'symbol' not in node:
                node=node.get((prefix>>(lookahead-used-1))&1)
                used+=1
                if node is None:break
            lookup.append((node,used))
        vals=[]
        for _ in range(count):
            node=tree
            if len(bits.data)*8-bits.pos>=lookahead:
                prefix=bits.read(lookahead)
                node,used=lookup[prefix]
                bits.pos-=lookahead-used
                if node is None:raise Huff816Error('unmatched entropy code')
            while 'symbol' not in node:
                bit=bits.read(1)
                if bit not in node:raise Huff816Error('unmatched entropy code')
                node=node[bit]
            vals.append(node['symbol'])
        stats['entropyBitsConsumed']=bits.pos
        consumed=bits.pos
    entropy=data[4+at:]
    if len(entropy)!=(consumed+31)//32*4:
        raise Huff816Error('entropy length differs from exact symbol consumption')
    padding=WordBits(entropy,consumed)
    while padding.pos<len(entropy)*8:
        if padding.read(min(32,len(entropy)*8-padding.pos)):
            raise Huff816Error('nonzero entropy padding')
    stats['entropyPaddingBits']=len(entropy)*8-consumed
    out=bytes(vals) if width==8 else struct.pack('<'+'H'*len(vals),*vals)
    return out,{'mode':'compressed','count':count,**stats}

def unwrap_24(lane:bytes,offset:int=4):
    """Locate Huff816 stream behind the 16-byte 0x24 family envelope."""
    if len(lane)<offset+20:raise Huff816Error('truncated 0x24 wrapper')
    h=struct.unpack_from('<I',lane,offset)[0]
    if h!=0x24000000:raise Huff816Error(f'not single-stream 0x24 wrapper: {h:08x}')
    return lane[offset+16:],{'wrapperU32':struct.unpack_from('<I',lane,offset+4)[0],
                              'wrapperU64':struct.unpack_from('<Q',lane,offset+8)[0]}

if __name__=='__main__':
    import sys
    sample=bytes.fromhex(sys.argv[1])
    for width in (8,16):
        try:print(width,parse_table(sample,width))
        except Exception as e:print(width,type(e).__name__,str(e))
