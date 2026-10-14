import assert from 'node:assert/strict';
import {TileStream} from '../viewer/independent/stream-controller.mjs';
import {frameAt,keyOf} from '../viewer/independent/stream-planner.mjs';

const turn=()=>new Promise(resolve=>setImmediate(resolve));
const tiles=[0,1,2].map(h=>({style:98,z:20,x:931325,y:412987,h}));
const originalFetch=globalThis.fetch;
try{
  let requests=0,loads=0,disposed=0;const releases=[];
  globalThis.fetch=async()=>{requests++;return {ok:true,json:async()=>({status:'ready',result:{}})};};
  const stream=new TileStream({frame:()=>frameAt(35.6586,139.7454),camera:()=>({position:[0,0,0],yaw:0,pitch:0,fov:1,aspect:1}),distance:()=>180,
    load:()=>{loads++;return new Promise(resolve=>releases.push(()=>resolve({cost:10})));},
    dispose:()=>disposed++,render:()=>{},status:()=>{},reduceDistance:()=>{}});
  stream.needed=new Map(tiles.map(t=>[keyOf(t),t]));stream.queue=tiles.slice();
  // Isolate asynchronous scheduling from camera planning, which has its own tests.
  stream.update=()=>stream.pump();stream.pump();await turn();
  assert.equal(requests,2);assert.equal(loads,2);assert.equal(stream.pending.size,2);
  stream.clear();stream.enabled=false;
  releases.forEach(release=>release());await turn();await turn();
  assert.equal(stream.models.size,0,'late results from the old location must never enter the scene');
  assert.equal(disposed,2,'cancelled model preparation must release both allocations');
  assert.equal(stream.pending.size,0);assert.ok(stream.cancelled>=2);

  let reductions=0,budgetDisposals=0;
  const budgeted=new TileStream({load:async()=>({cost:10}),dispose:()=>budgetDisposals++,render:()=>{},status:()=>{},reduceDistance:()=>reductions++});
  budgeted.budget=15;budgeted.needed=new Map(tiles.map(t=>[keyOf(t),t]));budgeted.queue=tiles.slice();budgeted.update=()=>budgeted.pump();
  budgeted.pump();for(let i=0;i<5;i++)await turn();
  assert.equal(budgeted.models.size,1);assert.equal(budgeted.bytes,10);assert.equal(budgetDisposals,2);assert.equal(reductions,2);
  assert.ok(budgeted.maxPending<=2);budgeted.clear();
  console.log('PASS: two-request limit, late-result cancellation/disposal, and model budget under concurrent completion');
}finally{globalThis.fetch=originalFetch;}
