const {chromium}=require('playwright-core');
(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
p.on('pageerror',e=>console.log('PAGEERROR',e.message));
p.on('console',m=>{if(m.type()==='error')console.log('CONSOLEERROR',m.text())});
p.on('requestfailed',r=>console.log('FAILED',r.url(),r.failure()?.errorText));
await p.goto('http://127.0.0.1:8891/',{waitUntil:'domcontentloaded'});
await p.waitForFunction(()=>window.__flyDebug?.nativeTrianglesMeta?.splatTrianglesVisible===417650,{timeout:60000});
await p.waitForTimeout(1300);
console.log('START',await p.locator('#status').innerText());
console.log('HYBRID',await p.evaluate(()=>{let d=window.__flyDebug;return {n:d.nativeTriangleMesh.geometry.attributes.position.count,triangles:d.nativeTrianglesMeta.splatTrianglesVisible,visible:d.nativeTriangleMesh.visible,pointApprox:d.nativeAll.visible,meshVisible:d.objects[0].visible,drawCalls:d.renderer.info.render.calls,drawTriangles:d.renderer.info.render.triangles,positionsXYZ:d.nativeTriangleMesh.geometry.getAttribute('position').array.slice(0,9).toString()}}));
await p.screenshot({path:'/tmp/apple-native-triangles-hybrid.png'});
await p.locator('#modeNativeOnly').click();await p.waitForTimeout(1200);
console.log('NATIVE_ONLY',await p.evaluate(()=>({triangles:window.__flyDebug.renderer.info.render.triangles,pointSprites:window.__flyDebug.renderer.info.render.points,groundVisible:window.__flyDebug.objects[0].visible,triangleVisible:window.__flyDebug.nativeTriangleMesh.visible})));
await p.screenshot({path:'/tmp/apple-native-triangles-only.png'});
await b.close();
})().catch(e=>{console.error('ERROR',e);process.exit(1)})