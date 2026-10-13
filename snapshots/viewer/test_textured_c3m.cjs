const {chromium}=require('playwright-core');
(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
p.on('console',m=>{if(m.type()==='error')console.log('JS-CONSOLE',m.text().slice(0,500))});
p.on('pageerror',e=>console.log('JS-ERROR',e.message));
p.on('requestfailed',req=>console.log('FETCH-FAILED',req.url(),req.failure()?.errorText));
await p.goto('http://127.0.0.1:8891/');
await p.waitForFunction(()=>window.__flyDebug?.c3mCache?.size>=21 || document.getElementById('c3mStatus')?.textContent.includes('失敗'),{timeout:70000});
await p.waitForTimeout(3000);
console.log('STATUS',await p.locator('#c3mStatus').innerText());
console.log('DEBUG',await p.evaluate(()=>{
 const d=window.__flyDebug;const meshes=Array.from(d.c3mCache.values());
 return {numTextures:meshes.filter(m=>m.material.map?.image).length,
  meshes:meshes.length,triangles:meshes.reduce((n,m)=>n+m.geometry.index.count/3,0),
  visibleOriginal:meshes.filter(m=>m.visible).length,
  texturesLoaded:meshes.filter(m=>m.material.map?.image?.naturalWidth>0).length,
  originalHybrid:d.c3mGroup.visible,proxyVisible:d.objects[0].visible,
  splatsVisible:d.nativeTriangleMesh.visible,
  render:d.renderer.info.render,
  camera:d.camera.position.toArray()
 };}));
await p.screenshot({path:'/tmp/apple-flyover-textured-c3m-hybrid.png'});
await b.close();
})().catch(e=>{console.log('TEST-ERROR',e.stack);process.exit(1)});
