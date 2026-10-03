#!/usr/bin/env python3
"""Real-browser check (optional). Needs: pip install playwright && playwright install chromium
Opens the home screen, Settings, the pocket reference, About, My progress and the Drill Night picker at phone sizes,
plus landscape and Daylight, and fails on any JavaScript error, anything off-screen, or a button under 44 px.
Usage: python3 tests/browser_check.py"""
import pathlib, sys
from playwright.sync_api import sync_playwright
URL = (pathlib.Path(__file__).resolve().parent.parent / 'index.html').as_uri()
OVER = "(()=>{let m=0;document.querySelectorAll('body *').forEach(e=>{if(e.offsetParent===null)return;const r=e.getBoundingClientRect();m=Math.max(m,r.right-window.innerWidth);});return Math.round(m);})()"
SMALL = "(()=>{let n=0;document.querySelectorAll('button').forEach(e=>{if(e.offsetParent===null)return;const r=e.getBoundingClientRect();if(r.width<2||r.height<2||r.bottom<0||r.top>innerHeight)return;if(r.height<44)n++;});return n;})()"
errs, rows = [], []
def tap(pg, sel):   # a slow tap, the way a finger does it: press, pause, release
    el = pg.locator(sel).first; el.scroll_into_view_if_needed(); pg.wait_for_timeout(80)
    b = el.bounding_box(); x, y = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
    pg.mouse.move(x, y); pg.mouse.down(); pg.wait_for_timeout(260); pg.mouse.up()
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (320, 390):
        pg = b.new_page(viewport={'width': w, 'height': 800}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(300); rows.append((w, 'home', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        tap(pg, '#h-learn'); pg.wait_for_timeout(200); rows.append((w, 'lesson', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL)))
        good = pg.evaluate("LESSON[LS.i].o.find(o=>o[1]==='good')[0]"); pg.locator('[data-l="ans"]', has_text=good).first.click(); pg.wait_for_timeout(120)
        tap(pg, '#l-next'); pg.wait_for_timeout(150); rows.append((w, 'lesson slide 2', pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.evaluate('LS.i') == 1 else 99))); tap(pg, '[data-l="quit"]')
        for did in ('placard', 'erg', 'container', 'nfpa704', 'zones', 'meter', 'shelter', 'ppe'):
            pg.goto(URL); pg.wait_for_timeout(150); tap(pg, f'[data-drill="{did}"]'); pg.wait_for_timeout(150)
            ans = pg.evaluate("QZ.qs[QZ.i].a"); pg.locator('[data-q="ans"]', has_text=ans).first.click(); pg.wait_for_timeout(120)
            rows.append((w, 'drill ' + did, pg.evaluate(OVER) + 1000 * pg.evaluate(SMALL) + (0 if pg.evaluate('QZ.right') == 1 else 99)))
        if w == 390:   # one drill to the end with real taps on the right answers, found by their visible text
            pg.goto(URL); pg.wait_for_timeout(150); tap(pg, '[data-drill="meter"]')
            for _ in range(8):
                ans = pg.evaluate("QZ.qs[QZ.i].a"); pg.locator('[data-q="ans"]', has_text=ans).first.click(); pg.wait_for_timeout(100); tap(pg, '[data-q="next"]'); pg.wait_for_timeout(100)
            rows.append((w, 'drill meter (full)', 0 if pg.evaluate('QZ.score') == 100 and pg.evaluate("JSON.parse(localStorage.getItem('upwind')).runs.length") >= 1 else 99)); pg.evaluate("localStorage.removeItem('upwind')")
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
