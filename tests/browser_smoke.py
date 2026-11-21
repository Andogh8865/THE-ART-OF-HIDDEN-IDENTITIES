#!/usr/bin/env python3
"""Actual headless browser smoke tests. Requires playwright + Chromium."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'logs'/'ui_tests.json'
checks=[]
def check(name,condition,details=''):
    checks.append({'name':name,'pass':bool(condition),'detail':details})
    print(('PASS' if condition else 'FAIL'),name,details)

def load_local(page, filename, jsname):
    markup=(ROOT/filename).read_text(encoding='utf-8')
    markup=re.sub(r'<link rel="stylesheet"[^>]+>', '', markup)
    markup=re.sub(r'<script src="[^"]+"></script>', '', markup)
    page.set_content(markup,wait_until='domcontentloaded')
    page.add_style_tag(content=(ROOT/'assets'/'style.css').read_text(encoding='utf-8'))
    page.add_script_tag(content=(ROOT/'assets'/jsname).read_text(encoding='utf-8'))

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox','--disable-gpu'])
    page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    load_local(page, 'index.html', 'app.js')
    check('title', 'Werewolf Academy' in page.title())
    check('10_slides',page.locator('.slide').count()==10)
    check('first_slide_visible',page.locator('#slide-1').evaluate('e=>e.classList.contains("active")'))
    page.screenshot(path=str(ROOT/'docs'/'preview_desktop.png'),full_page=True)
    page.locator('#nextSlide').click()
    check('navigation_next',page.locator('#slide-2').evaluate('e=>e.classList.contains("active")'))
    page.evaluate('window.WerewolfAcademy.showSlide(3)')
    card=page.locator('.role-card').first
    card.click()
    check('role_card_flip','flipped' in card.get_attribute('class'))
    page.evaluate('window.WerewolfAcademy.showSlide(6)')
    page.locator('#runNight').click()
    out=page.locator('#nightOutput').inner_text()
    check('double_save_result','同守同救' in out and '出局' in out,out[:70])
    page.screenshot(path=str(ROOT/'docs'/'preview_night_simulator.png'),full_page=True)
    page.locator('#previousGuard').select_option('6')
    page.locator('#runNight').click()
    check('guard_repeat_validation','行動無效' in page.locator('#nightOutput').inner_text())
    page.locator('#previousGuard').select_option('none')
    page.locator('#guardTarget').select_option('3')
    page.locator('#runNight').click()
    check('heal_only_survives','平安夜' in page.locator('#nightOutput').inner_text())
    page.locator('#witchAction').select_option('poison')
    page.locator('#runNight').click()
    check('poison_action', '9 號' in page.locator('#nightOutput').inner_text() and '毒' in page.locator('#nightOutput').inner_text())
    page.evaluate('window.WerewolfAcademy.showSlide(8)')
    page.locator('input[name="q1"][value="b"]').check()
    page.locator('input[name="q2"][value="b"]').check()
    page.locator('input[name="q3"][value="b"]').check()
    page.locator('#submitQuiz').click()
    check('quiz_3_of_3', '3 / 3' in page.locator('#quizResult').inner_text())
    check('no_js_errors',len(errors)==0,str(errors)[:180])
    load_local(page, 'wiki/index.html', 'wiki.js')
    check('wiki_18_entries',page.locator('.wiki-entry').count()==18)
    check('wiki_7_sources',page.locator('.source-row').count()==7)
    page.screenshot(path=str(ROOT/'docs'/'preview_wiki.png'),full_page=True)
    page.locator('#wikiSearch').fill('同守同救')
    check('wiki_search',page.locator('.wiki-entry:not(.hidden)').count()>=1 and page.locator('.wiki-entry:not(.hidden)').count()<18)
    check('no_wiki_js_errors',len(errors)==0,str(errors)[:180])
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    load_local(mobile, 'index.html', 'app.js')
    mobile.screenshot(path=str(ROOT/'docs'/'preview_mobile.png'),full_page=True)
    check('mobile_document_width',mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'),str(mobile.evaluate('document.documentElement.scrollWidth')))
    browser.close()

report={'at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'tests':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks),'result':'PASS' if all(x['pass'] for x in checks) else 'FAIL'}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'total':report['total'],'result':report['result']},ensure_ascii=False))
if report['result']!='PASS':raise SystemExit(1)
