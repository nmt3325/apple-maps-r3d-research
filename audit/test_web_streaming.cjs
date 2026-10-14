// Actual WebGL, camera movement, live server acquisition, and in-place relocation.
const {chromium}=require('../viewer/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
async function main(){
  const base=process.argv[2]||'http://127.0.0.1:8974';
  const output=path.resolve(process.argv[3]||'reports/generated/web-streaming-browser');fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',
    args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const checks=[],samples=[],errors=[],serverStates=[];let page;
  const check=(name,pass,evidence)=>{checks.push({name,pass:!!pass,evidence});if(!pass)throw Error(name);};
  try{
    page=await browser.newPage({viewport:{width:1440,height:1000}});
    if(process.env.R3D_TEST_UPSTREAM){
      const upstream=new URL(process.env.R3D_TEST_UPSTREAM);
      if(!['127.0.0.1','localhost'].includes(upstream.hostname))throw Error('QA upstream must be loopback');
      await page.route(base+'/**',async route=>{
        const target=new URL(route.request().url());target.protocol=upstream.protocol;target.host=upstream.host;
        const response=await route.fetch({url:target.href});await route.fulfill({response});
      });
    }
    page.on('pageerror',e=>errors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error'&&!/404|429/.test(m.text()))errors.push(m.text());});
    page.on('response',async r=>{if(r.url().endsWith('/api/stream/request')&&r.ok()){try{const s=await r.json();serverStates.push({tile:s.tile,status:s.status,cached:s.cached||false});}catch{}}});
    await page.goto(base+'/?lat=35.6586&lon=139.7454',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.r3dViewer?.snapshot().stream,{},{timeout:30000});
    const snapshot=()=>page.evaluate(()=>window.r3dViewer.snapshot());
    await page.locator('#distance').fill('180');await page.locator('#distance').dispatchEvent('input');
    await page.waitForFunction(()=>window.r3dViewer.snapshot().loaded>=3&&window.r3dViewer.snapshot().drawCalls>0,{},{timeout:120000});
    let s=await snapshot();samples.push({stage:'initial',...s});check('live geometry draws',s.triangles>0,s);
    await page.waitForFunction(()=>window.r3dViewer.snapshot().stream.lods.includes(20),{},{timeout:120000});
    s=await snapshot();samples.push({stage:'fine-lod',...s});check('coarse models refine to z20',s.stream.lods.includes(18)&&s.stream.lods.includes(20),s.stream.lods);
    check('upper heights loaded',s.stream.upperTiles>0,s.stream.upperTiles);
    await page.screenshot({path:path.join(output,'initial.png')});
    await page.locator('#fly').click();await page.locator('#speed').fill('150');await page.locator('#speed').dispatchEvent('input');
    await page.mouse.click(1100,500);
    const start=(await snapshot()).position;
    await page.keyboard.down('ShiftLeft');await page.keyboard.down('KeyD');
    try{await page.waitForFunction(p=>Math.hypot(...window.r3dViewer.snapshot().position.map((v,i)=>v-p[i]))>450,start,{timeout:30000});}
    finally{await page.keyboard.up('KeyD');await page.keyboard.up('ShiftLeft');}
    s=await snapshot();samples.push({stage:'move-450m',...s});
    check('WASD moves outside initial area',Math.hypot(...s.position.map((v,i)=>v-start[i]))>450,s.coordinate);
    const oldDesired=new Set(samples[0].stream.desired.map(t=>`${t.z}/${t.x}/${t.y}`));
    await page.waitForFunction(()=>window.r3dViewer.snapshot().stream.loaded>=3,{},{timeout:120000});
    s=await snapshot();check('camera replans destination tiles',s.stream.desired.some(t=>!oldDesired.has(`${t.z}/${t.x}/${t.y}`)),s.stream.desired);
    await page.mouse.click(1100,500);await page.waitForFunction(()=>window.r3dViewer.snapshot().pointerLocked,{},{timeout:10000});
    const before=(await snapshot()).quaternion;await page.mouse.move(2300,500);await page.waitForTimeout(400);
    s=await snapshot();check('mouse rotation changes view',Math.hypot(...s.quaternion.map((v,i)=>v-before[i]))>.1,s.quaternion);
    await page.keyboard.press('Escape');await page.screenshot({path:path.join(output,'moved.png')});
    // Let fine LODs finish; keep collecting resource statistics while requests run.
    for(let i=0;i<12;i++){await page.waitForTimeout(1000);samples.push({stage:'settling',...await snapshot()});}
    check('requests limited to two',samples.every(v=>v.stream.maxPending<=2),samples.map(v=>v.stream.maxPending));
    check('resident model budget respected',samples.every(v=>v.stream.residentBytes<=v.stream.budgetBytes),samples.map(v=>v.stream.residentBytes));
    await page.mouse.click(1100,500);
    await page.keyboard.down('ShiftLeft');await page.keyboard.down('KeyD');
    try{await page.waitForFunction(()=>window.r3dViewer.snapshot().rebases>0,{},{timeout:45000});}
    finally{await page.keyboard.up('KeyD');await page.keyboard.up('ShiftLeft');await page.keyboard.press('Escape');}
    s=await snapshot();samples.push({stage:'rebase-3km',...s});
    check('long travel rebases geographic origin',s.rebases>0&&Math.hypot(s.position[0],s.position[2])<1000&&Number.isFinite(s.coordinate.lat),s);
    await page.locator('#stream-enabled').uncheck();await page.waitForTimeout(1000);
    s=await snapshot();check('automatic acquisition can pause',!s.stream.enabled&&s.stream.pending===0,s.stream);
    await page.locator('#stream-enabled').check();
    // Location picker must keep the page and viewer alive, rather than open a batch scene.
    await page.locator('#pick-location').click();
    await page.locator('#pick-lat').fill('21.2828');await page.locator('#pick-lon').fill('-157.8369');await page.locator('#pick-radius').fill('160');
    await page.locator('#preview-area').click();await page.locator('#fetch-location').click();
    await page.waitForFunction(()=>window.r3dViewer.snapshot().origin[0]===21.2828&&window.r3dViewer.snapshot().loaded>=3,{},{timeout:180000});
    s=await snapshot();samples.push({stage:'waikiki',...s});
    check('arbitrary location loads in place',s.origin[1]===-157.8369&&new URL(page.url()).pathname==='/'&&s.drawCalls>0,s);
    check('previous location models released',s.stream.desired.every(t=>t.x<2**t.z/4),s.stream.desired);
    await page.screenshot({path:path.join(output,'waikiki.png')});
    await page.locator('#polygons').uncheck();await page.locator('#splats').uncheck();s=await snapshot();
    check('layer toggles preserved',!s.polygonsVisible&&!s.splatsVisible,s);await page.locator('#polygons').check();await page.locator('#splats').check();
    check('no JavaScript or shader errors',errors.length===0,errors);
  }finally{
    fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify({checks,samples,errors,serverStates},null,2)+'\n');
    await browser.close();
  }
  console.log(JSON.stringify({checks:checks.length,passed:checks.filter(c=>c.pass).length,errors}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
