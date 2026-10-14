from pathlib import Path
import numpy as np,struct,json
P=Path('/opt/flyover-viewer/decoded-native/all-223')
total=0;eq4=0;totrgba=np.zeros(4,int);mismatch={scale:np.zeros(4,int) for scale in [254.,255.,255.99,256.]};delts=[];last_words=0;last_mismatches=0
for gp in P.glob('*.decoded'):
 buf=gp.read_bytes(); n=struct.unpack_from('<I',buf,4)[0];material=np.fromfile(str(gp)[:-8]+'.native-material20',dtype=np.uint8).reshape(n,20)
 a=np.frombuffer(buf,dtype='<f4',count=n*8,offset=16+12*n).reshape(n,8)
 for scale in mismatch:
  expected=(np.floor(np.clip(a[:,[1,2,3,0]].astype('float64')*scale,0,255))).astype('u1')
  mismatch[scale]+=(expected != material[:,:4]).sum(axis=0)
 rgba_float=material[:,:4].astype('float64')/255.
 attr_order=a[:,[1,2,3,0]]
 d=rgba_float-attr_order
 delts.extend([float(d.min()),float(d.max())]);eq4+=int(np.count_nonzero(np.all(material[:,:4]==np.floor(np.clip(attr_order.astype('float64')*255,0,255)).astype('u1'),axis=1)))
 last = np.frombuffer(buf,dtype='<u4',count=n*8,offset=16+12*n).reshape(n,8)[:,4:8]
 ml=np.frombuffer(material[:,4:].copy(),dtype='<u4').reshape(n,4)
 last_mismatches+=int(np.count_nonzero(last!=ml));last_words+=n*4
 total+=n
print(json.dumps({'tiles':len(list(P.glob('*.decoded'))),'records':total,'rgba_floor_scale_mismatches':{str(k):v.tolist() for k,v in mismatch.items()},'record_all4_match_floor255':eq4,'last4attributes_float32_bitwise_mismatches':last_mismatches,'last4attributes_word_count':last_words,'material_minus_float_attribute_range':[min(delts),max(delts)]},indent=2))
