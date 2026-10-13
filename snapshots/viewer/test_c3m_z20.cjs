const {chromium}=require('playwright-core');(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1440,height:900}});
p.on('pageerror',e=>console.log('PAGEERROR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('JSERR',m.text().slice(0,500))});
await p.goto('http://127.0.0.1:8891/');
await p.waitForFunction(()=>window.__flyDebug?.c3mCache?.size>=21,{timeout:60000});
await p.locator('#c3mLOD').selectOption('20-near');
await p.waitForFunction(()=>document.getElementById('c3mStatus').textContent.includes('50タイル')&&document.getElementById('c3mStatus').textContent.includes('表示'),{},{timeout:120000}).catch(e=>console.log('WAIT',e.message));
await p.waitForTimeout(1000);
console.log('z20',await p.evaluate(()=>{const d=window.__flyDebug;let m=Array.from(d.c3mCache.values());return {status:document.getElementById('c3mStatus').textContent, visible:m.filter(x=>x.visible).length, loaded:m.length, tria:m.filter(x=>x.visible).reduce((v,x)=>v+x.geometry.index.count/3,0),textures:m.filter(x=>x.material.map.image?.naturalWidth>0).length,scene:d.renderer.info.render}}));
await p.screenshot({path:'/tmp/flyover-actual-c3m-z20-50tiles.png'});await b.close();
})().catch(e=>{console.log('Error',e.stack);process.exit(1)})