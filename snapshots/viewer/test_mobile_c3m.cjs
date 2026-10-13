const {chromium}=require('playwright-core');
(async()=>{
const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
p.on('pageerror',e=>console.log('PAGEERROR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text().slice(0,300))});
await p.goto('http://127.0.0.1:8891/');
await p.waitForFunction(()=>window.__flyDebug?.c3mCache?.size===21,{},{timeout:100000});
await p.waitForTimeout(2000);
console.log('mobile',await p.evaluate(()=>({window:innerWidth,sidebar:document.querySelector('aside').getBoundingClientRect().toJSON(),canvas:document.querySelector('#view').getBoundingClientRect().toJSON(),c3m:window.__flyDebug.c3mCache.size,triangles:window.__flyDebug.renderer.info.render.triangles,mode:window.__flyDebug.c3mGroup.visible})));
await p.screenshot({path:'/tmp/iphone-apple-maps-original-hybrid.png'});
await p.locator('#menuToggle').click();
await p.waitForTimeout(450);console.log('menuExpanded',await p.locator('#menuToggle').getAttribute('aria-expanded'));console.log('SIDE',await p.evaluate(()=>{let n=document.querySelector('aside'),c=getComputedStyle(n);return {rect:n.getBoundingClientRect().toJSON(),position:c.position,transform:c.transform,display:c.display,height:c.height,body:document.body.className,app:getComputedStyle(document.querySelector('#app')).height}}));
await p.screenshot({path:'/tmp/iphone-apple-maps-original-hybrid-menu.png'});
await b.close()})().catch(e=>{console.error(e);process.exit(1)});
