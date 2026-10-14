const { chromium } = require('../viewer/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

async function main(){
  const url=process.argv[2]||'http://127.0.0.1:8972/';
  const output=path.resolve(process.argv[3]||'reports/generated/oahu-browser');
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',
    args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
    await page.goto(url,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.r3dViewer?.snapshot().ready,{},{timeout:180000});
    await page.waitForTimeout(500);
    const snapshot=()=>page.evaluate(()=>window.r3dViewer.snapshot());
    const initial=await snapshot();
    await page.screenshot({path:path.join(output,'hybrid.png')});
    const checks=[];
    const assert=(name,condition,evidence)=>{checks.push({name,pass:!!condition,evidence});if(!condition)throw Error(name);};
    assert('all tiles loaded',initial.loaded>0&&initial.loaded===initial.polygonTiles&&initial.loaded===initial.splatTiles,initial);
    assert('WebGL draws original geometry',initial.drawCalls>0&&initial.triangles>0,initial);
    await page.locator('#splats').uncheck();let s=await snapshot();assert('Splat display toggle',!s.splatsVisible&&s.polygonsVisible,s);
    await page.screenshot({path:path.join(output,'polygons.png')});
    await page.locator('#splats').check();await page.locator('#polygons').uncheck();s=await snapshot();assert('polygon display toggle',s.splatsVisible&&!s.polygonsVisible,s);
    await page.screenshot({path:path.join(output,'splats.png')});await page.locator('#polygons').check();
    await page.locator('#fly').click();s=await snapshot();assert('free movement mode',s.flying,s);
    const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
    for(const key of ['w','a','s','d']){
      const before=await snapshot();await page.keyboard.down(key);
      try{await page.waitForFunction(({p})=>Math.hypot(...window.r3dViewer.snapshot().position.map((v,i)=>v-p[i]))>.1,{p:before.position},{timeout:30000});}
      finally{await page.keyboard.up(key);}const after=await snapshot();
      assert(`WASD ${key} changes position`,distance(before.position,after.position)>.1,{before:before.position,after:after.position});
    }
    for(const [key,sign] of [['e',1],['q',-1]]){
      const before=await snapshot();await page.keyboard.down(key);
      try{await page.waitForFunction(({y,sign})=>sign*(window.r3dViewer.snapshot().position[1]-y)>.1,{y:before.position[1],sign},{timeout:30000});}
      finally{await page.keyboard.up(key);}const after=await snapshot();
      assert(`vertical ${key}`,sign*(after.position[1]-before.position[1])>.1,{before:before.position,after:after.position});
    }
    await page.mouse.click(1000,500);await page.waitForTimeout(200);s=await snapshot();assert('mouse pointer lock acquired',s.pointerLocked,s);
    const before=await snapshot();await page.mouse.move(1100,550);await page.waitForTimeout(100);const after=await snapshot();
    assert('mouse view changes camera orientation',distance(before.quaternion,after.quaternion)>.001,{before:before.quaternion,after:after.quaternion});
    await page.keyboard.press('Escape');await page.waitForFunction(()=>!window.r3dViewer.snapshot().pointerLocked,{},{timeout:30000});s=await snapshot();assert('Escape releases mouse lock',!s.pointerLocked,s);
    await page.locator('#reset').click();await page.screenshot({path:path.join(output,'reset.png')});
    assert('no browser/shader errors',errors.length===0,errors);
    const report={url,initial,checks,errors,source:'Independently decoded R3D; actual browser UI events'};
    fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify({loaded:initial.loaded,checks:checks.length,passed:checks.filter(x=>x.pass).length,errors},null,2));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
