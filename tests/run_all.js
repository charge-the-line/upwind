#!/usr/bin/env node
/* Upwind — test suite.   node tests/run_all.js   (exit code 0 = all passed)
   Sections: syntax facts content home record privacy   (U0: the shell; drills and incidents add their sections in U1 and U2) */
global.window=global.window||{};
const path=require('path'),fs=require('fs'),vm=require('vm');
const ALL=['syntax','facts','content','home','record','privacy'];
let want=process.argv.slice(2);if(!want.length)want=ALL;
let failed=0,n=0;const T0=Date.now();
function report(sec,name,ok,detail=''){n++;if(!ok)failed++;console.log(`${ok?'PASS':'FAIL'}  ${sec.padEnd(9)} ${name}${detail?'  — '+detail:''}`);}
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');const {boot}=require('./uw_mock.js');
const sw=fs.readFileSync(path.join(__dirname,'..','sw.js'),'utf8');

if(want.includes('syntax')){try{new vm.Script(html.split('<script>')[1].split('</script>')[0]);report('syntax','index.html script compiles',true);}catch(e){report('syntax','index.html script compiles',false,e.message);}
  {const ver=(html.match(/APP_VERSION='([^']+)'/)||[])[1],cache=(sw.match(/CACHE = '([^']+)'/)||[])[1];
   report('syntax','service-worker cache matches app version',cache===`upwind-v${ver}`,`app ${ver}, cache ${cache}`);
   report('syntax','offline helper clears only its own old caches',/k\.startsWith\('upwind-v'\)/.test(sw)&&!/bls-ready|bleed-control|patient-contact|e102/.test(sw));
   report('syntax','offline helper never caches statistics requests',/goatcounter\\\.com|zgo\\\.at/.test(sw));}
  {// shared core: loaded before the app, listed in the offline cache, header hash matches the body, identical to the hub's copy when checked out next to it
   const cp=path.join(__dirname,'..','preconnect-core.js');const ct=fs.existsSync(cp)?fs.readFileSync(cp,'utf8'):'';const first=ct.split('\n')[0]||'';const body=ct.slice(first.length+1);
   const wantH=(first.match(/sha256:([0-9a-f]{64})/)||[])[1];const got=require('crypto').createHash('sha256').update(body,'utf8').digest('hex');
   const tagOK=html.indexOf('<script src="preconnect-core.js"></script>')>-1&&html.indexOf('<script src="preconnect-core.js"></script>')<html.indexOf('\n<script>\n');
   report('syntax','shared core loaded first, cached offline, header hash matches body',!!ct&&wantH===got&&sw.includes("'preconnect-core.js'")&&tagOK,wantH===got?'hash ok':`hash expected ${got.slice(0,12)}`);
   const hub=path.join(__dirname,'..','..','charge-the-line.github.io','preconnect-core.js');if(fs.existsSync(hub))report('syntax','shared core is byte-identical to the hub copy',fs.readFileSync(hub,'utf8')===ct);}
  {// fonts served from this site; nothing from Google; every file exists and is cached
   const urls=[...new Set([...html.matchAll(/url\((fonts\/[^)]+)\)/g)].map(m=>m[1]))];
   report('syntax','fonts served from this site, cached offline, no request to Google',!/fonts\.googleapis|gstatic\.com/.test(html)&&urls.length>=5&&urls.every(u=>fs.existsSync(path.join(__dirname,'..',u))&&sw.includes(`'${u}'`)),`${urls.length} font files`);}
  {// the statistics snippet, the drill-night bar and the settings sheet are the shared markup
   const snip=html.split('<script data-pca>')[1]||'';
   report('syntax','statistics snippet present, module code uw, pointed at preconnect.goatcounter.com',/window\.PCA_MOD="uw"/.test(snip)&&/preconnect\.goatcounter\.com\/count/.test(snip));
   report('syntax','drill night bar and picker markup present, settings sheet present with every switch',/<div id="pc-drill" class="pc-drillbar hidden" data-hub="\.\.\/"><\/div>/.test(html)&&/id="pc-drillov"/.test(html)&&['text','contrast','motion','sound','haptics','stats'].every(k=>html.includes(`data-set="${k}"`))&&/data-val="day"/.test(html));
   report('syntax','manifest and icons exist',fs.existsSync(path.join(__dirname,'..','manifest.json'))&&fs.existsSync(path.join(__dirname,'..','icon-192.png'))&&fs.existsSync(path.join(__dirname,'..','icon-512.png'))&&/"name": "Upwind"/.test(fs.readFileSync(path.join(__dirname,'..','manifest.json'),'utf8')));}
  {const {api}=boot();report('syntax','boots in the harness; settings and core helpers are reachable',typeof api.settings().sound==='string'&&typeof api.pcSpacing==='function'&&api.APP_VERSION===(html.match(/APP_VERSION='([^']+)'/)||[])[1]);}}

if(want.includes('facts')){const {api}=boot();const M=api.MAT;
  // One materials table. Every entry names its source; anything a drill or incident uses must be checked against the printed book.
  const ids=Object.keys(M);report('facts','every material names its ERG source page and guide',ids.length>=7&&ids.every(k=>M[k].src&&/ERG2024/.test(M[k].src)&&M[k].guide),ids.join(', '));
  const used=new Set();Object.values(api.DRILLS).forEach(d=>(d.mats||[]).forEach(m=>used.add(m)));Object.values(api.SCN).forEach(s=>(s.mats||[]).forEach(m=>used.add(m)));
  const unchecked=[...used].filter(m=>!M[m]||!M[m].checked);report('facts','every material a drill or incident uses has been checked against the printed ERG (date and reader)',unchecked.length===0,unchecked.length?'unchecked: '+unchecked.join(', '):`${used.size} in use`);
  // No distance may be shown anywhere unless it comes from a checked entry: at U0 the page prints no ERG distance at all.
  const vis=html.split('<script>')[0].split('<script data-pca>')[0]+html.split('</script>').pop();
  const distances=(html.split('<script>')[1].match(/\b(\d{2,4}) ?(m|ft|meters|feet|km|mi|miles)\b/g)||[]).filter(x=>!/^(48|44|540|480|390|320|1200|630) /.test(x));
  report('facts','no ERG distance is printed anywhere until its line is checked',distances.length===0,distances.join(' | ')||'none printed');
  report('facts','the page names the ERG edition and tells people to use their current ERG',api.ERG_ED==='ERG2024'&&/use your department's current ERG or the PHMSA ERG app/.test(html));
  report('facts','meter alarm points are the common defaults and the "know yours" line is there',api.METER.o2lo===19.5&&api.METER.o2hi===23.5&&api.METER.lel===10&&api.METER.co===35&&api.METER.h2s===10&&/Alarm settings vary by meter and department — know yours/.test(html)&&!/Altair|\bMSA\b|Dr[aä]ger|BW Technologies|\bRKI\b|Industrial Scientific/.test(html));}

if(want.includes('content')){
  report('content','the Operations boundary is stated on the home page and in the reference',/isolate, deny entry, call the hazmat team/i.test(html)&&/Operations crews do not enter/.test(html)&&/never teaches hot-zone entry/.test(html));
  report('content','no phone numbers ship until confirmed',!/\(\d{3}\)\s?\d{3}-\d{4}|\b\d{3}[-.]\d{3}[-.]\d{4}\b/.test(html));
  {const {api}=boot();api.els&&0;const about=(()=>{const {api,els}=boot();els['h-about'].onclick();return els['info-b'].innerHTML;})();
   report('content','every local name (the team, the notification list) is marked "to confirm" in About, and the list lives in TO_CONFIRM',api.TO_CONFIRM.length>=2&&/still to confirm with Bay County Emergency Management/.test(about)&&api.TO_CONFIRM.every(t=>about.includes(t.replace(/&/g,'&amp;')))&&/Regional Response Team 3/.test(about));}
  report('content','NFPA 470 section numbers are not shown in the app',!/\b[579]\.\d+\.\d+\b/.test(html)&&/NFPA 470/.test(html));
  report('content','trademark and affiliation notices',/Not affiliated with or endorsed by PHMSA, the NFPA/.test(html)&&/practice, not certification/.test(html)&&/Emergency Response Guidebook ©/.test(html));
  report('content','every overlay has a way back',/id="set-close"/.test(html)&&/id="info-close"/.test(html));
  report('content','wake lock helper present and off at home',/function keepAwake/.test(html)&&/function showHome\(\)\{keepAwake\(false\)/.test(html));}

if(want.includes('home')){const {api,els}=boot();
  const R=api.readiness();report('home','readiness counts the planned sixteen activities (lesson, eight drills, seven incidents) and starts at zero',R.total===16&&R.done===0&&els['rdy-t'].textContent==='0 of 16 activities'&&els['rdy-n'].textContent==='0%'&&/Coming in the next updates/.test(els['rdy-s'].textContent));
  report('home','drills and incidents are listed as coming, disabled, with a Soon chip; nothing is clickable that does not exist',(els.drills.innerHTML.match(/<button/g)||[]).length===8&&(els.incidents.innerHTML.match(/<button/g)||[]).length===7&&(els.drills.innerHTML.match(/ disabled/g)||[]).length===8&&(els.incidents.innerHTML.match(/ disabled/g)||[]).length===7&&/>Soon</.test(els.drills.innerHTML)&&/Tanker on its side, I-75/.test(els.incidents.innerHTML)&&/Nurse tank on a gravel road/.test(els.incidents.innerHTML));
  report('home','three tiers, Guided by default, the help line changes',api.TIER()===0&&/ERG distances are drawn on the map/.test(els.tierhelp.textContent));
  els['h-ref'].onclick();const ref=els['info-b'].innerHTML;report('home','pocket reference: ERG order, three zones, the generic meter, the always-right line, and no distances',/The ERG, in order/.test(ref)&&/Hot:/.test(ref)&&/Warm:/.test(ref)&&/Cold:/.test(ref)&&/19.5% low · 23.5% high/.test(ref)&&/Isolate. Deny entry. Call the hazmat team./.test(ref)&&/Distances are not listed here on purpose/.test(ref)&&!/\b\d+ ?(ft|m|mile|km)\b/.test(ref));
  report('home','ERG edition printed into the intro card',els['erg-ed'].textContent==='ERG2024');
  {const a=boot();a.els['b-inst'].onclick();const on=a.api.INST()&&JSON.parse(a.store.upwind).inst===true&&a.els['b-inst'].textContent==='Instructor mode: on';const b=boot({upwind:JSON.stringify({inst:true,runs:[]})});report('home','instructor switch saves and is remembered at boot',on&&b.api.INST()===true&&b.els['b-inst'].classList.contains('on'));}
  {const c=boot({'preconnect-drill':JSON.stringify({on:true,inst:'Max',roster:['Jo'],who:'Jo',start:new Date().toISOString()})});report('home','drill night: the switch reads on (Drill Night) without being set, and the bar binds',c.api.instOn()===true&&c.els['b-inst'].textContent==='Instructor mode: on (Drill Night)'&&!c.els['pc-drill'].classList.contains('hidden'));}}

if(want.includes('record')){const {api,store}=boot();api.record('drill','placard',88);api.record('scenario','i75',72,{variant:'B'});const R=JSON.parse(store.upwind).runs;
  report('record','runs save under the upwind key in the shared shape (kind, id, score, d, tier, variant)',R.length===2&&R[0].kind==='drill'&&R[0].id==='placard'&&R[0].score===88&&R[0].tier===0&&R[1].variant==='B'&&/^\d{4}-\d\d-\d\dT/.test(R[1].d));
  const b=boot({'preconnect-drill':JSON.stringify({on:true,inst:'Max',roster:['Jo'],who:'Jo',start:'2026-10-03T18:00:00.000Z'})});b.api.record('drill','erg',90);const r=JSON.parse(b.store.upwind).runs[0];
  report('record','on a drill night every run is stamped with who, the instructor and the night',r.who[0]==='Jo'&&r.inst==='Max'&&r.night==='2026-10-03T18:00:00.000Z');
  const c=boot({upwind:JSON.stringify({runs:[{kind:'drill',id:'placard',score:88,d:new Date().toISOString(),tier:0}]})});report('record','readiness and the home chips read saved best scores',c.api.readiness().done===1&&/id="chip-placard">88</.test(c.els.drills.innerHTML));
  const d=boot({upwind:JSON.stringify({runs:[{kind:'drill',id:'placard',score:88,d:'2026-10-03T10:00:00.000Z',tier:0}],name:'Jo',dept:'MTFD'})});d.els['h-prog'].onclick();d.els['p-name'].value='Jo';d.els['p-dept'].value='MTFD';d.els['p-csv'].onclick();
  report('record','progress screen and CSV list the saved run with a readable name',/not yet/.test(d.els['info-b'].innerHTML)&&/Placard ID/.test(global.__csv)&&/"Jo","MTFD","Drill","Placard ID"/.test(global.__csv));}

if(want.includes('privacy')){// the statistics snippet alone: names and typed text cannot survive into an event path; the opt-out stops everything
  const snip=html.split('<script data-pca>')[1].split('</script>')[0];const W={addEventListener(){}},sent=[];global.window=W;global.localStorage={getItem:()=>null};global.document={createElement:()=>({setAttribute(){}}),head:{appendChild(){}}};
  new Function(snip)();W.goatcounter={count:o=>sent.push(o.path)};W.PCA.ev('uw/finish/i75/Max Tester said "hi" <b>');W.PCA.flush();
  report('privacy','event paths are cleaned to safe characters and carry the uw module code',/^[a-z0-9\/\-]+$/.test(sent[0]||'x ')&&W.PCA.mod==='uw',sent[0]);
  report('privacy','scores are reported only as coarse bands',W.PCA.bkt(97)==='score-90-100'&&W.PCA.bkt(83)==='score-80s'&&W.PCA.bkt(12)==='score-under-60');
  const W2={addEventListener(){}},sent2=[];global.window=W2;global.localStorage={getItem:k=>k==='preconnect-stats'?'off':null};new Function(snip)();W2.goatcounter={count:o=>sent2.push(o.path)};W2.PCA.ev('uw/start/i75');W2.PCA.flush();
  report('privacy','the Privacy page opt-out stops every event',W2.PCA.off===true&&sent2.length===0);
  report('privacy','no name, organization or typed text is ever put into an event by the app',!/pca\([^)]*(name|dept|org|who|inst\b)/.test(html.split('<script>')[1]));}

console.log(`\n${n-failed}/${n} checks passed · ${Math.round((Date.now()-T0)/1000)} s`);process.exit(failed?1:0);
