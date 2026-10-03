// Bots that play an incident through runAct, the same handlers the buttons, the map taps and the handles use.
// Human pace: about 1.2 s per tap on the controllable clock (global.__T), with the tick run between taps.
const {boot}=require('./uw_mock.js');
function play(id,tier,o={}){global.__T=1000;const b=boot(Object.assign({upwind:JSON.stringify({runs:[]})},o.store||{}));const {api,els}=b;
  for(const k in api.MAT)api.MAT[k].checked='2026-10-03 test';standIn(api);if(o.variant)global.window.FORCE_V={[id]:o.variant};else delete global.window.FORCE_V;
  api.setTier(tier);api.runStart(id);const adv=s=>{global.__T+=s;api.runTick();};const tap=ds=>{adv(o.fast?.2:1.2);api.runAct(ds);api.runTick();};
  let g=0,teamCalled=false;const out={ok:false,score:null,steps:[],errs:[]};
  const fired=new Set();
  while(api.S()&&g++<80){const S=api.S(),s=S.def.steps[S.i];if(!s)break;out.steps.push(s.k+(s.id?':'+s.id:''));
    (o.injects||[]).forEach((j,n)=>{if(!fired.has(n)&&(j.at===s.k||j.at===s.id)){fired.add(n);api.instOpen();adv(j.hold||2);out.injected=(out.injected||[]).concat(api.inject(j.id));api.instClose();}});
    if(s.k==='approach'){const want=o.route||'good';const i=s.routes.findIndex(r=>r.kind===want);tap({r:'route',i:String(i)});continue;}
    if(s.k==='decide'){let kind=o.choice||'good';if(o.choiceAt&&o.choiceAt[s.id])kind=o.choiceAt[s.id];let i=s.o.findIndex(x=>x[1]===kind);if(i<0)i=s.o.findIndex(x=>x[1]==='good');tap({r:'opt',i:String(i)});if(!teamCalled&&!o.noTeam&&S.i>=2){tap({r:'team'});teamCalled=true;}if(o.dwell)adv(o.dwell);tap({r:'next'});continue;}
    if(s.k==='bino'){s.items.forEach((it,i)=>{if(it.need&&!o.binoMiss)tap({r:'bino',i:String(i)});if(!it.need&&o.binoWrong)tap({r:'bino',i:String(i)});});tap({r:'binook'});continue;}
    if(s.k==='erg'){const i=s.opts.findIndex(x=>x[1]===(o.ergWrong?'bad':'good'));tap({r:'erg',i:String(i)});tap({r:'next'});continue;}
    if(s.k==='zones'){const iso=api.MAT[S.def.mat].iso.ft;const wantHot=o.hot!==undefined?o.hot:iso+10,wantWarm=o.warm!==undefined?o.warm:wantHot+60;
      while(S.z.hot<wantHot)tap({r:'nudge',z:'hot',d:'25'});while(S.z.hot>wantHot+24)tap({r:'nudge',z:'hot',d:'-25'});while(S.z.warm<wantWarm)tap({r:'nudge',z:'warm',d:'25'});
      const dir=o.stageDownwind?(api.WX.dir+180)%360:o.stageCross?(api.WX.dir+90)%360:api.WX.dir;const v=api.vec(dir);const dist=(o.stageInside?S.z.warm*.6:S.z.warm+40)/S.scale;tap({r:'stage',x:String(S.R.x+v.x*dist),y:String(S.R.y+v.y*dist)});
      if(o.waitBeforeZones)adv(o.waitBeforeZones);tap({r:'zonesok'});continue;}
    if(s.k==='notify'){s.items.forEach((it,i)=>{if(it.need&&!o.notifyMiss&&!(o.notifySkipTeam&&it.id==='team'))tap({r:'chk',i:String(i)});if(!it.need&&o.notifyExtra)tap({r:'chk',i:String(i)});});tap({r:'notifyok'});continue;}
    break;}
  out.ok=!!els.doneov&&!els.doneov.classList.contains('hidden');out.score=+els['done-s'].textContent;out.body=els['done-b'].innerHTML;out.store=b.store;out.api=api;out.els=els;return out;}
// Test stand-ins for green-page rows Max has not read yet. These are NOT ERG values; the page keeps iso:null and the incident locked until the real row is stamped.
function standIn(api){const a=api.MAT.ammonia;if(!a.iso)a.iso={m:0,ft:200,standIn:true};if(!a.t3)a.t3={nurse:{day:{low:.2,mod:.3,high:.4},night:{low:.7,mod:1,high:1.5}},standIn:true};}
module.exports={play,standIn};
