// Camera/LOD/height planning mirrors ios/App/World.swift, without WebGL dependencies.
const A=6378137, ESQ=6.6943799901413165e-3, RAD=Math.PI/180;
export const keyOf=t=>`${t.style??98}/${t.z}/${t.x}/${t.y}/${t.h??0}`;
export const horizontal=t=>({...t,style:98,h:0});
export const rootOf=t=>({style:98,z:18,x:t.x>> (t.z-18),y:t.y>> (t.z-18),h:0});
export const indexOf=t=>({style:100,z:13,x:t.x>> (t.z-13),y:t.y>> (t.z-13),h:0});
export const wrapLongitude=lon=>((lon+180)%360+360)%360-180;
export function validCoordinate(lat,lon){return Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=85.05112878&&Math.abs(lon)<=180;}
function ecef(lat,lon){const p=lat*RAD,l=lon*RAD,n=A/Math.sqrt(1-ESQ*Math.sin(p)**2);return [n*Math.cos(p)*Math.cos(l),n*Math.cos(p)*Math.sin(l),n*(1-ESQ)*Math.sin(p)];}
export function frameAt(lat,lon){
  if(!validCoordinate(lat,lon))throw Error('緯度・経度が範囲外です');
  const p=lat*RAD,l=lon*RAD;
  return {lat,lon,ecef:ecef(lat,lon),basis:[[-Math.sin(l),Math.cos(l),0],[Math.cos(p)*Math.cos(l),Math.cos(p)*Math.sin(l),Math.sin(p)],[Math.sin(p)*Math.cos(l),Math.sin(p)*Math.sin(l),-Math.cos(p)]]};
}
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function worldPoint(frame,lat,lon){const xyz=ecef(lat,lon).map((v,i)=>v-frame.ecef[i]);return frame.basis.map(row=>dot(row,xyz));}
export function coordinateAt(frame,position){
  const [x,y,z]=frame.ecef.map((v,i)=>v+frame.basis.reduce((s,row,k)=>s+row[i]*position[k],0));
  const p=Math.hypot(x,y);let lat=Math.atan2(z,p*(1-ESQ));
  for(let i=0;i<8;i++){const n=A/Math.sqrt(1-ESQ*Math.sin(lat)**2),h=p/Math.cos(lat)-n;lat=Math.atan2(z,p*(1-ESQ*n/(n+h)));}
  return {lat:Math.max(-85.05112878,Math.min(85.05112878,lat/RAD)),lon:wrapLongitude(Math.atan2(y,x)/RAD)};
}
export function tileCoordinate(t,dx=.5,dy=.5){const n=2**t.z;return {lat:Math.atan(Math.sinh(Math.PI*(1-2*(t.y+dy)/n)))/RAD,lon:(t.x+dx)/n*360-180};}
export function tileCenter(frame,t){const c=tileCoordinate(t);return worldPoint(frame,c.lat,c.lon);}
export function tileBounds(frame,t){
  const points=[0,1].flatMap(dx=>[0,1].map(dy=>{const c=tileCoordinate(t,dx,dy);return worldPoint(frame,c.lat,c.lon);}));
  return [Math.min(...points.map(p=>p[0])),Math.max(...points.map(p=>p[0])),Math.min(...points.map(p=>p[2])),Math.max(...points.map(p=>p[2]))];
}
export function tileMatrix(frame,transform){
  const r=transform.matrixR3x3,t=transform.ecefTranslation;
  if(r?.length!==9||t?.length!==3||![...r,...t].every(Number.isFinite))throw Error('タイルの位置情報が不正です');
  const m=frame.basis.map(row=>[0,1,2].map(col=>row.reduce((s,v,k)=>s+v*r[3*k+col],0)));
  const shift=frame.basis.map(row=>dot(row,t.map((v,i)=>v-frame.ecef[i])));
  return [m[0][0],m[1][0],m[2][0],0,m[0][1],m[1][1],m[2][1],0,m[0][2],m[1][2],m[2][2],0,...shift,1];
}
export function planTiles(frame,camera,distance=250){
  distance=Math.max(80,Math.min(600,distance));
  const location=coordinateAt(frame,camera.position),n=2**18;
  const xx=Math.floor((location.lon+180)/360*n),yy=Math.floor((1-Math.asinh(Math.tan(location.lat*RAD))/Math.PI)/2*n);
  const width=z=>2*Math.PI*A*Math.cos(location.lat*RAD)/2**z;
  const radius=Math.ceil(distance/width(18))+1;
  const halfFOV=Math.atan(Math.tan(camera.fov/2)*Math.max(1,camera.aspect));
  const [east,south]=[Math.sin(camera.yaw),-Math.cos(camera.yaw)],leaves=[];
  function visit(t){
    const center=tileCenter(frame,t),dx=center[0]-camera.position[0],dz=center[2]-camera.position[2];
    const length=Math.hypot(dx,dz),diagonal=width(t.z)*.71;
    if(length-diagonal>distance)return;
    if(length>diagonal+90&&camera.pitch>-.9){
      const angle=Math.acos(Math.max(-1,Math.min(1,(dx*east+dz*south)/length)));
      if(angle>halfFOV+.35+Math.asin(Math.min(1,diagonal/length)))return;
    }
    if(t.z<20&&Math.max(0,length-diagonal)<(t.z===18?200:85)){
      for(let dy=0;dy<2;dy++)for(let dx=0;dx<2;dx++)visit({style:98,z:t.z+1,x:t.x*2+dx,y:t.y*2+dy,h:0});
    }else leaves.push(t);
  }
  for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
    const y=yy+dy;if(y>=0&&y<n)visit({style:98,z:18,x:((xx+dx)%n+n)%n,y,h:0});
  }
  return leaves.sort((a,b)=>{const ca=tileCenter(frame,a),cb=tileCenter(frame,b);return Math.hypot(ca[0]-camera.position[0],ca[2]-camera.position[2])-Math.hypot(cb[0]-camera.position[0],cb[2]-camera.position[2]);}).slice(0,192);
}
export function expandHeights(index,t){
  const expected=indexOf(t);
  if(index.tile?.z!==13||index.tile.x!==expected.x||index.tile.y!==expected.y||!Array.isArray(index.cells))throw Error('高さインデックスの座標が一致しません');
  const factor=2**(t.z-17),x=Math.floor(t.x/factor)%16,y=15-Math.floor(t.y/factor)%16;
  const heights=new Set();
  for(const cell of index.cells){
    if(cell.length!==3||!cell.every(Number.isInteger)||cell[2]<0)throw Error('高さインデックスが不正です');
    if(cell[0]===x&&cell[1]===y)for(let child=0;child<factor;child++)heights.add(factor*cell[2]+child);
  }
  if(heights.size>384)throw Error('高さ層が取得上限を超えました');
  return [...heights].sort((a,b)=>a-b).map(h=>({...t,h}));
}
export function selectLOD(desired,expanded,available){
  const roots=new Map(desired.map(t=>{const r=rootOf(t);return [keyOf(r),r];})),selected=new Set(),masks=new Map();
  const complete=t=>{const children=expanded.get(keyOf(t));return children!==undefined&&children.every(c=>available(keyOf(c)));};
  for(const [rootKey,root] of roots){
    const leaves=desired.filter(t=>keyOf(rootOf(t))===rootKey),fine=leaves.filter(t=>t.z>18&&complete(t));
    if(!leaves.every(complete)){
      // Show each prepared coarse height immediately while the rest arrives.
      for(const t of expanded.get(rootKey)||[])if(available(keyOf(t)))selected.add(keyOf(t));
      masks.set(rootKey,fine);
    }
    for(const leaf of leaves)if(complete(leaf))for(const t of expanded.get(keyOf(leaf))||[])selected.add(keyOf(t));
  }
  return {selected,masks};
}
