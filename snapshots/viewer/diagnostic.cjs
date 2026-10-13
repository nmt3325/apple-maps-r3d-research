const {chromium}=require('playwright-core');
(async()=>{
let b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1400,height:900},deviceScaleFactor:1});
p.on('console',x=>console.log('CONSOLE',x.type(),x.text().slice(0,400)));
p.on('pageerror',e=>console.log('PAGEERROR',e.message.slice(0,1500)));
p.on('requestfailed',r=>console.log('FAILED',r.url(),r.failure()?.errorText));
await p.goto('http://127.0.0.1:8891/');
await p.waitForTimeout(3500);
console.log('STATUS',await p.locator('#status').innerText());
console.log('CANVAS',await p.locator('canvas').count()); console.log('DEBUG',await p.evaluate(()=>{const d=window.__flyDebug;if(!d)return 'missing';let mesh=d.objects[0],pos=mesh.geometry.getAttribute('position');return {camera:d.camera.position.toArray(),cameraDir:d.camera.getWorldDirection(new (d.camera.position.constructor)()).toArray(),target:d.ctrl.target.toArray(),sceneSize:d.scene.children.length,points:d.points.length,terrains:d.terrains.length,firstVert:[pos.getX(0),pos.getY(0),pos.getZ(0)],middleVert:[pos.getX(32768),pos.getY(32768),pos.getZ(32768)],renderer:d.renderer.info.render,viewSize:[d.renderer.domElement.width,d.renderer.domElement.height]}}));
console.log('SCREEN',await p.locator('#view').boundingBox());
console.log('WEBGL',await p.evaluate(()=>{const c=document.querySelector('canvas');return c ? {width:c.width,height:c.height,firstpixel:Array.from(c.getContext('webgl2')?.readPixels ? []:[])} : 'none'}));
await p.locator('#splats').check(); await p.waitForTimeout(1500); console.log('SPLAT',await p.evaluate(()=>({clouds:window.__flyDebug.splatClouds?.length,visible:window.__flyDebug.splatClouds?.filter(x=>x.visible).length,frames:window.__flyDebug.renderer.info.render}))); await p.screenshot({path:'/tmp/flyover-gaussian-splats.png'});
await b.close();
})().catch(e=>{console.error('EXCEPTION',e);process.exit(1)});
