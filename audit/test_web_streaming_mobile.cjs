const {chromium}=require('../viewer/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
async function main(){
  const base=process.argv[2]||'http://127.0.0.1:8974',output=path.resolve(process.argv[3]||'reports/generated/web-streaming-mobile');fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const checks=[],errors=[];let final;
  const assert=(name,pass,evidence)=>{checks.push({name,pass:!!pass,evidence});if(!pass)throw Error(name);};
  try{
    const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
    if(process.env.R3D_TEST_UPSTREAM){
      const upstream=new URL(process.env.R3D_TEST_UPSTREAM);
      if(!['127.0.0.1','localhost'].includes(upstream.hostname))throw Error('QA upstream must be loopback');
      await page.route(base+'/**',async route=>{
        const target=new URL(route.request().url());target.protocol=upstream.protocol;target.host=upstream.host;
        const response=await route.fetch({url:target.href});await route.fulfill({response});
      });
    }
    page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error'&&!/404|429/.test(m.text()))errors.push(m.text());});
    await page.goto(base+'/?lat=35.6586&lon=139.7454');
    await page.waitForFunction(()=>window.r3dViewer?.snapshot().loaded>=2&&window.r3dViewer.snapshot().drawCalls>0,{},{timeout:120000});
    const snapshot=()=>page.evaluate(()=>window.r3dViewer.snapshot());
    let s=await snapshot();assert('mobile model budget is 96 MiB',s.stream.budgetBytes===96*1024*1024,s.stream);
    assert('mobile controls initially collapsed',await page.locator('#panel-toggle').getAttribute('aria-expanded')==='false',true);
    await page.locator('#panel-toggle').tap();assert('mobile settings can expand',await page.locator('#distance').isVisible(),true);await page.locator('#panel-toggle').tap();
    await page.screenshot({path:path.join(output,'mobile.png')});
    const cdp=await page.context().newCDPSession(page);
    const button=await page.locator('[data-move="KeyW"]').boundingBox();assert('touch movement control visible',button&&button.x>=0&&button.y+button.height<=844,button);
    const initial=s.position;
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:button.x+button.width/2,y:button.y+button.height/2}]});
    try{await page.waitForFunction(p=>Math.hypot(...window.r3dViewer.snapshot().position.map((v,i)=>v-p[i]))>3,initial,{timeout:15000});}
    finally{await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});}
    s=await snapshot();assert('touch control moves camera without pointer lock',s.flying&&!s.pointerLocked&&Math.hypot(...s.position.map((v,i)=>v-initial[i]))>3,s.position);
    const released=s.position;await page.waitForTimeout(500);s=await snapshot();assert('releasing touch stops movement',Math.hypot(...s.position.map((v,i)=>v-released[i]))<.5,s.position);
    const quaternion=s.quaternion;
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:330,y:400}]});
    await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:370,y:430}]});
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    s=await snapshot();assert('touch drag rotates camera',Math.hypot(...s.quaternion.map((v,i)=>v-quaternion[i]))>.03,s.quaternion);
    assert('mobile memory remains bounded',s.stream.residentBytes<=s.stream.budgetBytes,s.stream.residentBytes);
    assert('no mobile JavaScript or shader errors',errors.length===0,errors);final=s;
  }finally{fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify({checks,errors,final},null,2)+'\n');await browser.close();}
  console.log(JSON.stringify({checks:checks.length,passed:checks.filter(c=>c.pass).length,errors}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
