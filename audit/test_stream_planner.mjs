import assert from 'node:assert/strict';
import {frameAt,coordinateAt,worldPoint,tileMatrix,planTiles,keyOf,rootOf,indexOf,expandHeights,selectLOD} from '../viewer/independent/stream-planner.mjs';

for(const [lat,lon] of [[35.6586,139.7454],[21.2828,-157.8369],[0,179.9999],[84.9,-179.9999],[-84.9,0]]){
  const frame=frameAt(lat,lon),c=coordinateAt(frame,[0,0,0]);
  assert.ok(Math.abs(c.lat-lat)<1e-8);assert.ok(Math.abs(c.lon-lon)<1e-8);
  const shifted=coordinateAt(frame,[450,0,300]),point=worldPoint(frame,shifted.lat,shifted.lon);
  assert.ok(Math.abs(point[0]-450)<.2);assert.ok(Math.abs(point[2]-300)<.2);
  const camera={position:[0,100,160],yaw:0,pitch:-.45,fov:Math.PI/3,aspect:1.4};
  const plan=planTiles(frame,camera,350);
  assert.ok(plan.length>0&&plan.length<=192);assert.equal(new Set(plan.map(keyOf)).size,plan.length);
  for(const t of plan){assert.ok(t.x>=0&&t.x<2**t.z&&t.y>=0&&t.y<2**t.z);assert.ok([18,19,20].includes(t.z));assert.equal(indexOf(t).z,13);}
  for(const t of plan)for(const other of plan)if(other.z<t.z)assert.ok(!(t.x>>(t.z-other.z)===other.x&&t.y>>(t.z-other.z)===other.y),'quadtree leaves must not overlap');
}
const frame=frameAt(35.6586,139.7454),camera={position:[0,100,160],yaw:0,pitch:-.45,fov:Math.PI/3,aspect:1.4};
const initial=planTiles(frame,camera,350),moved=planTiles(frame,{...camera,position:[450,100,160]},350),rotated=planTiles(frame,{...camera,yaw:Math.PI},350);
assert.deepEqual([...new Set(initial.map(t=>t.z))].sort(),[18,19,20]);
assert.notDeepEqual(initial,moved);assert.notDeepEqual(initial,rotated);
const matrix=tileMatrix(frame,{matrixR3x3:[1,0,0,0,1,0,0,0,1],ecefTranslation:frame.ecef});
assert.deepEqual(matrix.slice(12),[0,0,0,1]);
for(const z of [18,19,20]){
  const factor=2**(z-17),tile={style:98,z,x:7*2**(z-13)+2*factor,y:8*2**(z-13)+2*factor,h:0};
  const index={tile:{z:13,x:7,y:8},cells:[[2,13,0],[2,13,3]]};
  const children=expandHeights(index,tile);
  assert.deepEqual(children.map(t=>t.h),[...Array(factor).keys(),...Array.from({length:factor},(_,i)=>3*factor+i)]);
  assert.throws(()=>expandHeights({...index,tile:{z:13,x:8,y:8}},tile));
}
const root={style:98,z:18,x:2,y:3,h:0},a={style:98,z:19,x:4,y:6,h:0},b={style:98,z:19,x:5,y:6,h:0};
const coarse=[root,{...root,h:1}],fine=[a,{...a,h:1}],expanded=new Map([[keyOf(root),coarse],[keyOf(a),fine],[keyOf(b),[b]]]);
const available=new Set([keyOf(root),keyOf(a)]);
let selection=selectLOD([a,b],expanded,id=>available.has(id));
assert.deepEqual([...selection.selected],[keyOf(root)]);assert.equal(selection.masks.get(keyOf(root)).length,0);
available.add(keyOf({...a,h:1}));selection=selectLOD([a,b],expanded,id=>available.has(id));
assert.ok(selection.selected.has(keyOf(root)));assert.ok(selection.selected.has(keyOf(a)));assert.deepEqual(selection.masks.get(keyOf(root)),[a]);
available.add(keyOf(b));selection=selectLOD([a,b],expanded,id=>available.has(id));assert.ok(!selection.selected.has(keyOf(root)));
assert.equal(keyOf(rootOf(a)),keyOf(root));
console.log('PASS: geographic transforms, dateline/polar bounds, camera movement/rotation, quadtree partition, z13 height expansion, progressive LOD masks');
