const {chromium}=require('playwright-core');
(async()=>{
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1470,height:930}});
page.on('pageerror',e=>console.log('PAGEERROR',e.message));
page.on('requestfailed',r=>console.log('REQFAIL',r.url()));
await page.goto('http://127.0.0.1:8891/');
await page.waitForFunction(()=>window.__flyDebug?.nativePoints);
const dat=await page.evaluate(()=>{
 const d=window.__flyDebug;
 return {nativeCount:d.nativePoints.geometry.getAttribute('position').count,visible:d.nativePoints.visible,
 nativeBounds:d.nativeMeta.minimum.concat(d.nativeMeta.maximum),
 nativeRender:d.renderer.info.render,
 compareMesh:d.objects.length};});
console.log('NATIVE',JSON.stringify(dat));
await page.locator('#focusNative').click();
await page.waitForTimeout(2800);
console.log('TARGET',JSON.stringify(await page.evaluate(()=>window.__flyDebug.ctrl.target.toArray())));
console.log('DRAW',JSON.stringify(await page.evaluate(()=>window.__flyDebug.renderer.info.render)));
await page.screenshot({path:'/tmp/flyover-native-splats-verified.png'});
await browser.close();
})().catch(e=>{console.error(e);process.exit(1)})