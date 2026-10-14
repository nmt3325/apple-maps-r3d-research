import {keyOf,rootOf,indexOf,planTiles,expandHeights,tileCenter,selectLOD} from './stream-planner.mjs';

const sleep=(ms,signal)=>new Promise((resolve,reject)=>{
  if(signal.aborted){reject(new DOMException('Aborted','AbortError'));return;}
  const abort=()=>{clearTimeout(timer);reject(new DOMException('Aborted','AbortError'));};
  const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},ms);
  signal.addEventListener('abort',abort,{once:true});
});

class PreparationSlots {
  constructor(limit){this.limit=limit;this.active=0;this.waiters=[];}
  acquire(signal){
    return new Promise((resolve,reject)=>{
      if(signal.aborted){reject(new DOMException('Aborted','AbortError'));return;}
      const waiter={grant:()=>{signal.removeEventListener('abort',abort);resolve();}};
      const abort=()=>{const index=this.waiters.indexOf(waiter);if(index>=0)this.waiters.splice(index,1);reject(new DOMException('Aborted','AbortError'));};
      if(this.active<this.limit){this.active++;resolve();}
      else {this.waiters.push(waiter);signal.addEventListener('abort',abort,{once:true});}
    });
  }
  async run(signal,operation){
    await this.acquire(signal);
    try{
      if(signal.aborted)throw new DOMException('Aborted','AbortError');
      return await operation();
    }finally{
      if(this.waiters.length)this.waiters.shift().grant();else this.active--;
    }
  }
}

export class TileStream {
  constructor(options){
    this.options=options;this.models=new Map();this.indices=new Map();this.empty=new Map();this.failures=new Map();this.pending=new Map();
    this.epoch=0;this.active=true;this.enabled=true;this.authFailed=false;this.error='';this.queue=[];this.desired=[];this.expanded=new Map();this.needed=new Map();
    this.lastPlan=0;this.completed=0;this.evictions=0;this.cancelled=0;this.maxPending=0;this.bytes=0;this.budget=192*1024*1024;
    this.preparation=new PreparationSlots(2);
  }
  clear(){
    this.epoch++;for(const p of this.pending.values()){p.controller.abort();this.cancelled++;}this.pending.clear();
    for(const entry of this.models.values())this.options.dispose(entry.model);
    this.models.clear();this.indices.clear();this.empty.clear();this.failures.clear();this.queue=[];this.needed.clear();this.expanded.clear();this.desired=[];
    this.bytes=0;this.completed=0;this.lastPlan=0;this.error='';this.authFailed=false;
  }
  setActive(value){this.active=value;if(!value){for(const p of this.pending.values())p.controller.abort();}else this.lastPlan=0;}
  retry(){this.failures.clear();this.authFailed=false;this.error='';this.lastPlan=0;}
  tick(now){
    if(!this.enabled||!this.active||this.authFailed)return;
    if(now-this.lastPlan>=250){this.lastPlan=now;this.update(now);}
  }
  update(now=performance.now()){
    if(!this.enabled||!this.active)return;
    const frame=this.options.frame(),camera=this.options.camera();
    this.desired=planTiles(frame,camera,this.options.distance());
    const horizontal=new Map();
    for(const t of this.desired){horizontal.set(keyOf(t),t);const r=rootOf(t);horizontal.set(keyOf(r),r);}
    const indices=new Map([...horizontal.values()].map(t=>{const i=indexOf(t);return [keyOf(i),i];}));
    this.needed=new Map(indices);this.expanded=new Map();
    for(const [id,index] of this.indices){if(!indices.has(id)&&now-index.touched>20000)this.indices.delete(id);}
    for(const t of horizontal.values()){
      const index=this.indices.get(keyOf(indexOf(t)));
      if(!index)continue;index.touched=now;
      try{const candidates=expandHeights(index.result,t);this.expanded.set(keyOf(t),candidates);for(const c of candidates)this.needed.set(keyOf(c),c);}
      catch(error){this.error=error.message;this.failures.set(keyOf(indexOf(t)),now+20000);this.indices.delete(keyOf(indexOf(t)));}
    }
    for(const [id,p] of this.pending)if(!this.needed.has(id)&&!p.controller.signal.aborted){p.controller.abort();this.cancelled++;}
    for(const cache of [this.empty,this.failures])for(const [id,until] of cache)if(until<=now||!this.needed.has(id))cache.delete(id);
    if(!this.failures.size&&!this.authFailed)this.error='';
    for(const [id,entry] of this.models){
      if(this.needed.has(id))entry.touched=now;
      else if(now-entry.touched>2000)this.evict(id);
    }
    this.trim(0);
    const roots=new Set(this.desired.map(t=>keyOf(rootOf(t))));
    const rank=t=>{if(t.style===100)return -10000;const c=tileCenter(frame,t),dx=c[0]-camera.position[0],dz=c[2]-camera.position[2],d=Math.hypot(dx,dz);
      const alignment=d>0?(dx*Math.sin(camera.yaw)-dz*Math.cos(camera.yaw))/d:1;
      return (roots.has(keyOf({...t,h:0}))?-5000:0)+d+(1-alignment)*120+t.h*.01;};
    this.queue=[...this.needed.values()].filter(t=>{const id=keyOf(t);return !this.pending.has(id)&&!this.models.has(id)&&!this.empty.has(id)&&!this.failures.has(id)&&!this.indices.has(id);}).sort((a,b)=>rank(a)-rank(b));
    this.draw();this.pump();this.notify();
  }
  evict(id){const entry=this.models.get(id);if(!entry)return;this.bytes-=entry.cost;this.options.dispose(entry.model);this.models.delete(id);this.evictions++;}
  trim(reserving){
    const victims=[...this.models].filter(([id])=>!this.needed.has(id)).sort((a,b)=>a[1].touched-b[1].touched);
    for(const [id] of victims)if(this.bytes+reserving>this.budget)this.evict(id);
  }
  draw(){
    const selection=selectLOD(this.desired,this.expanded,id=>this.models.has(id)||this.empty.has(id));
    for(const [id,entry] of this.models){const root=keyOf(rootOf(entry.tile));this.options.render(entry.model,selection.selected.has(id),entry.tile.z===18?(selection.masks.get(root)||[]):[]);}
  }
  pump(){
    while(this.enabled&&this.active&&!this.authFailed&&this.pending.size<4&&[...this.pending.values()].filter(p=>p.acquiring).length<2&&this.queue.length){
      const tile=this.queue.shift(),id=keyOf(tile),epoch=this.epoch,controller=new AbortController(),pending={controller,acquiring:true};
      this.pending.set(id,pending);this.maxPending=Math.max(this.maxPending,this.pending.size);
      this.run(tile,controller.signal,epoch,()=>{pending.acquiring=false;this.pump();}).catch(error=>{
        if(epoch!==this.epoch||error.name==='AbortError')return;
        if(error.authenticationFailed){this.authFailed=true;for(const p of this.pending.values())p.controller.abort();}
        this.error=error.message;this.failures.set(id,performance.now()+(error.status===429?1000:20000));
      }).finally(()=>{
        if(this.pending.get(id)===pending)this.pending.delete(id);
        if(epoch===this.epoch&&this.enabled&&this.active&&!this.authFailed)this.update();
        this.notify();
      });
    }
  }
  async run(tile,signal,epoch,acquired){
    const id=keyOf(tile);
    const read=async response=>{const body=await response.json();if(!response.ok)throw Object.assign(Error(body.error||'タイルを読み込めません'),{status:response.status,authenticationFailed:body.authenticationFailed});return body;};
    let state=await read(await fetch('/api/stream/request',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(tile),signal}));
    while(state.status==='queued'){
      await sleep(400,signal);
      state=await read(await fetch(`/api/stream/jobs/${state.id}`,{signal,cache:'no-store'}));
    }
    if(signal.aborted||epoch!==this.epoch)throw new DOMException('Aborted','AbortError');
    if(state.status==='failed')throw Object.assign(Error(state.message||'取得・復号に失敗しました'),{authenticationFailed:state.authenticationFailed});
    if(state.status==='empty'){this.empty.set(id,performance.now()+60000);return;}
    if(state.status!=='ready'||!state.result)throw Error('タイルの応答が不正です');
    if(tile.style===100){this.indices.set(id,{result:state.result,touched:performance.now()});return;}
    acquired();
    await this.preparation.run(signal,async()=>{
      const model=await this.options.load(state.result,signal);
      if(signal.aborted||epoch!==this.epoch||!this.needed.has(id)){this.options.dispose(model);return;}
      const cost=model.cost;this.trim(cost);
      if(this.bytes+cost>this.budget){this.options.dispose(model);this.options.reduceDistance();throw Error('メモリに合わせて表示範囲を縮小しました');}
      this.models.set(id,{model,cost,tile,touched:performance.now()});this.bytes+=cost;this.completed++;
      if(!this.failures.size)this.error='';
    });
  }
  notify(){this.options.status(this.snapshot());}
  snapshot(){return {enabled:this.enabled,active:this.active,loaded:this.models.size,pending:this.pending.size,queued:this.queue.length,
    completed:this.completed,evictions:this.evictions,cancelled:this.cancelled,maxPending:this.maxPending,
    acquiring:[...this.pending.values()].filter(p=>p.acquiring).length,preparing:this.preparation.active,residentBytes:this.bytes,budgetBytes:this.budget,
    lods:[...new Set([...this.models.values()].map(e=>e.tile.z))].sort(),upperTiles:[...this.models.values()].filter(e=>e.tile.h>0).length,
    desired:this.desired.map(t=>({...t})),error:this.error,authFailed:this.authFailed};}
}
