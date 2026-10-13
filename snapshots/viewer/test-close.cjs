const {chromium}=require('playwright-core');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:900}});
 p.on('pageerror',e=>console.log('error',e.message));
 await p.goto('http://127.0.0.1:8891/');
 await p.waitForFunction(()=>window.__flyDebug?.nativeTriangleMesh,{timeout:60000});
 await p.locator('#focusCloseNative').click();
 await p.waitForTimeout(2000);
 console.log('nativeClose',await p.evaluate(()=>({camera:window.__flyDebug.camera.position.toArray(),target:window.__flyDebug.ctrl.target.toArray(),polyMesh:window.__flyDebug.objects[0].visible,triangleMesh:window.__flyDebug.nativeTriangleMesh.visible,depthSort:document.getElementById('sortTriangleState').textContent})));
 await p.screenshot({path:'/tmp/apple-native-close-view.png'});
 await b.close();
})().catch(e=>{console.log(e);process.exit(1)})
