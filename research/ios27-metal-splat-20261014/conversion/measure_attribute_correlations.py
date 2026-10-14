import numpy as np,struct
from pathlib import Path
p=next(Path('/opt/flyover-viewer/decoded-native/all-223').glob('*.decoded'))
raw=p.read_bytes();n=struct.unpack_from('<I',raw,4)[0]
a=np.frombuffer(raw,dtype='<f4',offset=16+12*n,count=8*n).reshape(n,8)
v=np.fromfile(str(p)[:-8]+'.native-triangle-f32',dtype='<f4').reshape(3,n,3).transpose(1,0,2)
e1=v[:,1]-v[:,0];e2=v[:,2]-v[:,0];area=np.linalg.norm(np.cross(e1,e2),axis=1)*.5
mask=(a[:,0]>0)&np.isfinite(a).all(axis=1)
print('file',p.name,'visible',int(mask.sum()))
for i in range(5):print(i,a[i].round(4).tolist(),e1[i].round(3).tolist(),e2[i].round(3).tolist(),round(float(area[i]),2))
for label,x in [('area',area),('len01',np.linalg.norm(e1,axis=1)),('len02',np.linalg.norm(e2,axis=1))]:
 print(label,'corr with attr4..7:',[round(float(np.corrcoef(a[mask,j],x[mask])[0,1]),3) for j in range(4,8)])
