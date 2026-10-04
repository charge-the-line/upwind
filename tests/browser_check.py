#!/usr/bin/env python3
"""Real-browser check (optional). Needs: pip install playwright && playwright install chromium
Opens the home screen, Settings, the pocket reference, About, My progress and the Drill Night picker at phone sizes,
plus landscape and Daylight, and fails on any JavaScript error, anything off-screen, or a button under 44 px.
Usage: python3 tests/browser_check.py"""
import pathlib, re, sys
from playwright.sync_api import sync_playwright
URL = (pathlib.Path(__file__).resolve().parent.parent / 'index.html').as_uri()
OVER = "(()=>{let m=0;document.querySelectorAll('body *').forEach(e=>{if(e.offsetParent===null)return;const r=e.getBoundingClientRect();m=Math.max(m,r.right-window.innerWidth);});return Math.round(m);})()"
SMALL = "(()=>{let n=0;document.querySelectorAll('button').forEach(e=>{if(e.offsetParent===null)return;const r=e.getBoundingClientRect();if(r.width<2||r.height<2||r.bottom<0||r.top>innerHeight)return;if(r.height<44)n++;});return n;})()"
errs, rows = [], []
def tap(pg, sel):   # a slow tap, the way a finger does it: press, pause, release
    el = pg.locator(sel).first; el.scroll_into_view_if_needed(); pg.wait_for_timeout(80)
    b = el.bounding_box(); x, y = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
    pg.mouse.move(x, y); pg.mouse.down(); pg.wait_for_timeout(260); pg.mouse.up()
def incident(pg, w, scn, pre, unlock=None, force=None):   # play an incident with real taps, a real drag and a map tap; unlock is a JS snippet for a locked incident (test stand-ins, never ERG values)
    pg.goto(URL); pg.wait_for_timeout(150)
    if unlock: pg.evaluate(unlock)
    if force: pg.evaluate("window.FORCE_V={%s:'%s'}" % (scn, force))
    tap(pg, '[data-scn="%s"]' % scn); pg.wait_for_timeout(600)
    rows.append((w, pre + 'approach', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
    good = pg.evaluate("S.def.steps[0].routes.find(r=>r.kind==='good').name"); pg.locator('[data-r="route"]', has_text=good).first.click(); pg.wait_for_timeout(600)
    ans = pg.evaluate("S.def.steps[S.i].o.find(o=>o[1]==='good')[0]"); pg.locator('[data-r="opt"]', has_text=re.compile('^' + re.escape(ans) + '$')).first.click(); pg.wait_for_timeout(150); rows.append((w, pre + 'decision', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '[data-r="next"]'); pg.wait_for_timeout(600)
    for lab in pg.evaluate("S.def.steps[S.i].items.filter(x=>x.need).map(x=>x.label)"): pg.locator('[data-r="bino"]', has_text=lab).first.click(); pg.wait_for_timeout(80)
    rows.append((w, pre + 'binoculars', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '[data-r="binook"]'); pg.wait_for_timeout(600)
    ans = pg.evaluate("S.def.steps[S.i].opts.find(o=>o[1]==='good')[0]"); pg.locator('[data-r="erg"]', has_text=ans).first.click(); pg.wait_for_timeout(150); tap(pg, '[data-r="next"]'); pg.wait_for_timeout(600)
    if pg.evaluate("S.def.steps[S.i].k") == 'zones':   # an indoor incident (the white powder) has no zones step
        rows.append((w, pre + 'zones', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        # drag the hot handle outward the way a finger does, then tap the map upwind for staging, then nudge warm with the buttons
        pg.locator('#uw-svg').scroll_into_view_if_needed(); pg.wait_for_timeout(80)   # a long step text can leave the map above the viewport
        svg = pg.locator('#uw-svg').bounding_box(); hb = pg.locator('#mh-hot').bounding_box(); cx, cy = svg['x'] + svg['width'] * 150 / 340, svg['y'] + svg['height'] * 140 / 300
        hx, hy = hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2; dx, dy = hx - cx, hy - cy; d = (dx * dx + dy * dy) ** .5
        pg.mouse.move(hx, hy); pg.mouse.down(); pg.wait_for_timeout(120)
        for k in range(1, 25):
            pg.mouse.move(cx + dx / d * (d + k * 8), cy + dy / d * (d + k * 8)); pg.wait_for_timeout(40)
            if pg.evaluate("S.z.hot >= MAT[S.def.mat].iso.ft"): break
        pg.mouse.up(); pg.wait_for_timeout(100)
        rows.append((w, pre + 'drag hot ring', 0 if pg.evaluate("S.z.hot >= MAT[S.def.mat].iso.ft*0.95 && S.z.hot <= MAT[S.def.mat].iso.ft*2.5") else 99))
        while pg.evaluate("S.z.warm < S.z.hot+40"): tap(pg, '[data-r="nudge"][data-z="warm"][data-d="25"]')
        upx, upy = pg.evaluate("(()=>{const v=vec(WX.dir),d=(S.z.warm+40)/S.scale;return [S.R.x+v.x*d,S.R.y+v.y*d];})()")   # a tap upwind, just outside the warm ring
        pg.locator('#uw-svg').scroll_into_view_if_needed(); pg.wait_for_timeout(80); svg = pg.locator('#uw-svg').bounding_box()   # the nudge taps may have scrolled the top of the map away
        pg.mouse.move(svg['x'] + svg['width'] * upx / 340, svg['y'] + svg['height'] * upy / 300); pg.mouse.down(); pg.wait_for_timeout(200); pg.mouse.up(); pg.wait_for_timeout(100)
        rows.append((w, pre + 'staging by tap', 0 if pg.evaluate("zoneFit(S.z,WX.dir,MAT[S.def.mat].iso.ft).ok") else 99))
        tap(pg, '[data-r="zonesok"]'); pg.wait_for_timeout(600)
    for _ in range(12):
        k = pg.evaluate("S?S.def.steps[S.i].k:null")
        if k is None: break
        if k == 'decide':
            ans = pg.evaluate("S.def.steps[S.i].o.find(o=>o[1]==='good')[0]"); pg.locator('[data-r="opt"]', has_text=re.compile('^' + re.escape(ans) + '$')).first.click(); pg.wait_for_timeout(150); tap(pg, '[data-r="next"]'); pg.wait_for_timeout(600)
        elif k == 'notify':
            for lab in pg.evaluate("S.def.steps[S.i].items.filter(x=>x.need).map(x=>x.label)"): pg.locator('[data-r="chk"]', has_text=lab).first.click(); pg.wait_for_timeout(80)
            tap(pg, '[data-r="notifyok"]'); pg.wait_for_timeout(600)
        else: break
    pg.wait_for_timeout(800)
    rows.append((w, pre + '(full)', 0 if pg.is_visible('#doneov') and pg.text_content('#done-s') == '100' else 99)); pg.evaluate("localStorage.removeItem('upwind')")

with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (320, 390):
        pg = b.new_page(viewport={'width': w, 'height': 800}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(300); rows.append((w, 'home', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        tap(pg, '#h-learn'); pg.wait_for_timeout(200); rows.append((w, 'lesson', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        good = pg.evaluate("LESSON[LS.i].o.find(o=>o[1]==='good')[0]"); pg.locator('[data-l="ans"]', has_text=re.compile('^' + re.escape(good) + '$')).first.click(); pg.wait_for_timeout(120)
        tap(pg, '#l-next'); pg.wait_for_timeout(150); rows.append((w, 'lesson slide 2', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.evaluate('LS.i') == 1 else 99))); tap(pg, '[data-l="quit"]')
        for did in ('placard', 'erg', 'container', 'nfpa704', 'zones', 'meter', 'shelter', 'ppe'):
            pg.goto(URL); pg.wait_for_timeout(150); tap(pg, f'[data-drill="{did}"]'); pg.wait_for_timeout(150)
            ans = pg.evaluate("QZ.qs[QZ.i].a"); pg.locator('[data-q="ans"]', has_text=re.compile('^' + re.escape(ans) + '$')).first.click(); pg.wait_for_timeout(120)
            rows.append((w, 'drill ' + did, pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.evaluate('QZ.right') == 1 else 99)))
        if w == 390:   # one drill to the end with real taps on the right answers, found by their visible text
            pg.goto(URL); pg.wait_for_timeout(150); tap(pg, '[data-drill="meter"]')
            for _ in range(8):
                ans = pg.evaluate("QZ.qs[QZ.i].a"); pg.locator('[data-q="ans"]', has_text=re.compile('^' + re.escape(ans) + '$')).first.click(); pg.wait_for_timeout(100); tap(pg, '[data-q="next"]'); pg.wait_for_timeout(100)
            rows.append((w, 'drill meter (full)', 0 if pg.evaluate('QZ.score') == 100 and pg.evaluate("JSON.parse(localStorage.getItem('upwind')).runs.length") >= 1 else 99)); pg.evaluate("localStorage.removeItem('upwind')")
        incident(pg, w, 'i75', 'incident ')
        if w == 390: incident(pg, w, 'nurse', 'nurse tank ', force='C')
        if w == 320: incident(pg, w, 'propane', 'refill cage ', force='B'); incident(pg, w, 'house', 'house ', force='B')
        if w == 390: incident(pg, w, 'pool', 'swim club ', force='A')
        if w == 390: incident(pg, w, 'rail', 'rail car ', force='A')
        if w == 320: incident(pg, w, 'rail', 'rail car fire ', force='B')
        if w == 390: incident(pg, w, 'powder', 'white powder ', force='A')
        if w == 320: incident(pg, w, 'powder', 'white powder sick ', force='C')
        if w == 390:   # instructor mode: switch on, open the incident, the floating button opens the sheet, an inject lands, freeze and resume, quit
            pg.goto(URL); pg.wait_for_timeout(150); tap(pg, '#b-inst'); tap(pg, '[data-scn="i75"]'); pg.wait_for_timeout(600)
            good = pg.evaluate("S.def.steps[0].routes.find(r=>r.kind==='good').name"); pg.locator('[data-r="route"]', has_text=good).first.click(); pg.wait_for_timeout(600)   # the wind inject waits until the crew is on scene
            tap(pg, '#inst-fab'); pg.wait_for_timeout(200); rows.append((w, 'instructor sheet', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.is_visible('#instov') and pg.evaluate('S.frozenAt!==null') else 99)))
            tap(pg, '[data-inj="wind"]'); pg.wait_for_timeout(200); landed = pg.evaluate("S.injects.length===1 && S.frozenAt===null && WX.target!==null")
            tap(pg, '#inst-fab'); pg.wait_for_timeout(150); tap(pg, '[data-inj="freeze"]'); pg.wait_for_timeout(150); froze = pg.evaluate("INSTHOLD && S.frozenAt!==null") and 'Frozen' in pg.text_content('#inst-fab')
            tap(pg, '#inst-fab'); pg.wait_for_timeout(150); resumed = pg.evaluate("!INSTHOLD && S.frozenAt===null")
            rows.append((w, 'instructor inject + freeze', 0 if landed and froze and resumed else 99)); tap(pg, '[data-r="quit"]'); pg.wait_for_timeout(300); pg.evaluate("localStorage.removeItem('upwind')")
        pg.goto(URL); pg.wait_for_timeout(150); tap(pg, '#h-set'); pg.wait_for_timeout(150); rows.append((w, 'settings', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '#set-close')
        tap(pg, '#h-ref'); pg.wait_for_timeout(150); rows.append((w, 'reference', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '#info-close')
        tap(pg, '#h-about'); pg.wait_for_timeout(150); rows.append((w, 'about', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '#info-close')
        tap(pg, '#h-prog'); pg.wait_for_timeout(150); rows.append((w, 'progress', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '#info-close')
        tap(pg, '[data-tier="2"]'); pg.wait_for_timeout(100); rows.append((w, 'chaos tier', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if 'Chaos' in pg.text_content('#tierhelp') else 99)))
        tap(pg, '#b-inst'); pg.wait_for_timeout(100); rows.append((w, 'instructor switch', 0 if 'on' in pg.text_content('#b-inst') else 99)); tap(pg, '#b-inst')
        pg.evaluate("localStorage.setItem('preconnect-drill',JSON.stringify({on:true,inst:'Max',roster:['Jo','Sam'],who:'',start:new Date().toISOString()}))"); pg.goto(URL); pg.wait_for_timeout(300); rows.append((w, 'drill picker', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        tap(pg, '.pc-drill-name'); pg.wait_for_timeout(200); rows.append((w, 'drill night', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if 'Drill Night' in pg.text_content('#b-inst') else 99)))
        pg.evaluate("localStorage.removeItem('preconnect-drill')")
        pg.evaluate("localStorage.setItem('preconnect-settings',JSON.stringify({text:'large'}))"); pg.goto(URL); pg.wait_for_timeout(300); rows.append((w, 'large text', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        pg.evaluate("localStorage.setItem('preconnect-settings',JSON.stringify({contrast:'day'}))"); pg.goto(URL); pg.wait_for_timeout(300); rows.append((w, 'daylight', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        pg.evaluate("localStorage.removeItem('preconnect-settings')")
        pg.goto(URL + '?drill=placard'); pg.wait_for_timeout(300); rows.append((w, 'daily link', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.is_visible('#quizov') else 99)))
        pg.close()
    pg = b.new_page(viewport={'width': 844, 'height': 390}, device_scale_factor=2, is_mobile=True, has_touch=True); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(300); rows.append((844, 'landscape', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
    tap(pg, '#h-set'); pg.wait_for_timeout(150); rows.append((844, 'settings land', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL))); tap(pg, '#set-close')
    b.close()
bad = 0
for w, name, v in rows:
    over, small = v % 1000, v // 1000
    ok = over <= 0 and small == 0
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {w}px  {name:<32} overflow {over}px · buttons under 44px: {small}")
print('JavaScript errors:', errs or 'none')
sys.exit(1 if bad or errs else 0)
