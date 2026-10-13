const {chromium}=require('playwright-core');(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:900}});
p.on('pageerror',e=>console.error('PAGE ERROR',e.message));
await p.goto('http://127.0.0.1:8891/');
await p.waitForFunction(()=>window.__flyDebug?.nativeTrianglesMeta?.splatTrianglesVisible===417650,{timeout:60000});
await p.waitForTimeout(3500);
console.log('sort-check',await p.evaluate(()=>{const d=window.__flyDebug;return {label:document.getElementById('sortTriangleState').textContent, indices:Array.from(d.nativeTriangleMesh.geometry.index.array.slice(0,25)),sorted:!d.nativeTriangleMesh.geometry.index.array.slice(0,25).every((v,i)=>v===i),camera:d.camera.position.toArray(),target:d.ctrl.target.toArray()}}));
await p.locator('#sortNativeTriangles').uncheck();await p.waitForTimeout(500);
console.log('sort-off',await p.evaluate(()=>Array.from(window.__flyDebug.nativeTriangleMesh.geometry.index.array.slice(0,12))));
await p.locator('#sortNativeTriangles').check();await p.waitForTimeout(1200);
console.log('sort-on',await p.evaluate(()=>({label:document.getElementById('sortTriangleState').textContent,index:Array.from(window.__flyDebug.nativeTriangleMesh.geometry.index.array.slice(0,12))})));
await b.close()})().catch(e=>{console.error(e);process.exit(1)})