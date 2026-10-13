const {chromium}=require('playwright-core');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 page.on('pageerror',e=>console.log('PAGEERR',e.message));
 await page.goto('http://127.0.0.1:8891/');
 await page.waitForFunction(()=>window.__flyDebug?.c3mCache?.size>=21,{},{timeout:75000});
 const tile='r3d_z19_x465662_y206403_h0';
 for(const flip of [false,true]){
   await page.evaluate(({flip,tile})=>{
    const d=window.__flyDebug;
    d.nativeTriangleMesh.visible=false;d.nativeAll.visible=false;
    d.c3mGroup.visible=true;
    for(const mesh of d.c3mCache.values()){
      mesh.visible=mesh.userData.tile.id===tile;
      mesh.material.map.flipY=flip;
      mesh.material.map.needsUpdate=true;
    }
    d.ctrl.target.set(-95.1,62.0,215.2);
    d.camera.position.set(-95.1+85,62.0+70,215.2+95);
    d.ctrl.update();
   },{flip,tile});
   await page.waitForTimeout(1400);
   console.log('sample '+flip,await page.evaluate(()=>({calls:window.__flyDebug.renderer.info.render.calls,triangles:window.__flyDebug.renderer.info.render.triangles,uv:window.__flyDebug.c3mCache.get('r3d_z19_x465662_y206403_h0').geometry.attributes.uv.array.slice(0,20).toString()})));
   await page.screenshot({path:'/tmp/c3m_uv_flipY_'+flip+'.png'});
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
