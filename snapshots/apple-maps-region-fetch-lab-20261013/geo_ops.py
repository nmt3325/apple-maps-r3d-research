import numpy as np,struct,math
def project(positions,raw,x0,y0):
 p=raw.find(bytes.fromhex('01010100016a'))
 if p<0:raise ValueError('No transform')
 R=np.array(struct.unpack_from('<9d',raw,p+6)).reshape(3,3)
 E=np.array(struct.unpack_from('<3d',raw,p+78))
 xyz=positions.reshape(-1,3).astype('float64')@R.T+E
 x,y,z=xyz.T;r=np.hypot(x,y);esq=6.69437999014e-3
 lon=np.arctan2(y,x);lat=np.arctan2(z,r*(1-esq))
 for _ in range(5):
  n=6378137/np.sqrt(1-esq*np.sin(lat)**2)
  h=r/np.cos(lat)-n
  lat=np.arctan2(z,r*(1-esq*n/(n+h)))
 n=6378137/np.sqrt(1-esq*np.sin(lat)**2)
 h=r/np.cos(lat)-n
 mx=(np.degrees(lon)+180)/360*16384
 my=(1-np.arcsinh(np.tan(lat))/np.pi)/2*16384
 ref=math.degrees(math.atan(math.sinh(math.pi*(1-2*(y0+.5)/16384))))
 units=40075016.686*math.cos(math.radians(ref))/16384
 return np.stack([(mx-x0)*units,h,(my-y0)*units],axis=-1).astype('<f4')
