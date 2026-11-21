#!/usr/bin/env python3
"""Build two static sites from the SAME verified source-linked wiki records."""
from __future__ import annotations
import html
import json
from pathlib import Path


def e(s):
    return html.escape(str(s), quote=True)


def build_site(root: Path):
    data = json.loads((root / "data" / "verified_claims.json").read_text(encoding="utf-8"))
    corpus = json.loads((root / "data" / "source_evidence.json").read_text(encoding="utf-8"))
    by_key = {r["key"]:r for r in data}
    sources = {s["id"]:s for s in corpus["sources"]}

    def proof(key):
        r = by_key[key]
        links = ' · '.join(f'<a href="wiki/index.html#{e(r["id"])}" title="開啟此規則與來源">{e(s)}</a>' for s in r["source_ids"])
        return f'<span class="proof" title="來源可追溯">{e(r["id"])} · {links}</span>'

    def cite_rule(key):
        r = by_key[key]
        return f'<div class="claim-line"><span>{e(r["explanation"])}</span>{proof(key)}</div>'

    roles = [
        ("🐺","狼人","WOLF","晚上選一位玩家為攻擊目標，白天隱藏身分。","werewolf_kill"),
        ("👑","狼王","WOLF","遭正常淘汰時可帶走一名玩家；被女巫毒則不行。","alpha_death_shot"),
        ("🔮","預言家","GOOD","每晚驗一人的陣營，幫助好人蒐集資訊。","seer_check"),
        ("🧪","女巫","GOOD","一瓶解藥與一瓶毒藥；每晚最多用一瓶。","witch_potions"),
        ("🏹","獵人","GOOD","被狼人刀或被票出能開槍；被女巫毒不能。","hunter_poison_shot"),
        ("🛡️","守衛","GOOD","每晚守一位玩家；不能連守同一人。","guard_repeat"),
        ("🧑‍🌾","平民","GOOD","沒有夜間技能，靠討論與投票找出狼人。","villager_ability"),
    ]
    role_markup = '\n'.join(f'''<button type="button" class="role-card" data-role="{e(n)}" aria-label="翻開{e(n)}角色卡" aria-pressed="false">
      <span class="role-face role-front"><span class="role-symbol">{emoji}</span><span class="role-name">{e(n)}</span><span class="role-know">點我翻牌 ↗</span></span>
      <span class="role-face role-back"><span class="role-type {faction.lower()}">{'狼人陣營' if faction=='WOLF' else '好人陣營'}</span><strong>{e(n)}</strong><span class="role-description">{e(desc)}</span><span class="role-proof">{e(by_key[k]['id'])} · {', '.join(by_key[k]['source_ids'])}</span></span>
    </button>''' for emoji,n,faction,desc,k in roles)

    rule_data = {r["key"]: {k:r[k] for k in ["id","title","explanation","source_ids","value","board"]} for r in data}
    slides_html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07111f"><meta name="description" content="狼人殺互動教學：角色翻牌、夜晚結算、測驗與來源對照。">
<title>Werewolf Academy｜狼人殺互動教學簡報</title><link rel="stylesheet" href="assets/style.css"></head>
<body class="slides-view"><div class="app-shell">
<header class="topbar"><a class="brand" href="index.html"><span class="brand-mark">☾</span><span>WEREWOLF<span class="brand-accent">/</span>ACADEMY</span></a><div class="top-actions"><a class="subtle-link" href="wiki/index.html">知識庫 <span aria-hidden="true">↗</span></a><button type="button" id="fullscreen" class="icon-btn" title="全螢幕">⛶</button></div></header>
<main class="deck" id="deck">
<section class="slide active" id="slide-1" data-title="Welcome" aria-label="簡報第1頁">
 <div class="hero-stage"><div class="halo"></div><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="wolf-glyph" aria-hidden="true">☽</div></div>
 <div class="eyebrow">AN INTERACTIVE FIELD GUIDE <span class="eyebrow-dot">✦</span> 12 PLAYER EDITION</div>
 <h1 class="hero-title">THE ART OF<br><em>HIDDEN IDENTITIES.</em></h1>
 <p class="lead center">從零學會狼人殺。理解角色，走過一個夜晚，完成你的第一場推理。</p>
 <div class="hero-actions"><button class="primary-btn" data-next>開始探索 <span>↗</span></button><a class="text-btn" href="wiki/index.html">閱讀規則 Wiki →</a></div>
 <div class="hero-meta"><span>10 教學章節</span><span>7 個資料來源</span><span>3 種互動練習</span></div>
</section>
<section class="slide" id="slide-2" data-title="遊戲目標" aria-label="簡報第2頁"><div class="slide-intro"><div class="eyebrow">01 / THE CORE IDEA</div><h2>一場關於<span class="accent">身分與信任</span>的遊戲。</h2><p class="lead">每人拿到一張只有自己知道的角色牌。狼人試圖混入人群；好人靠資訊、討論與投票找出他們。</p></div>
 <div class="two-up"><div class="feature-card wolf-panel"><span class="big-emoji">🐺</span><span class="faint-label">SHADOW FACTION</span><h3>狼人陣營</h3><p>夜晚共同選定目標，白天偽裝成好人。</p><div class="feature-number">4 <small>PLAYERS</small></div></div><div class="feature-card village-panel"><span class="big-emoji">✨</span><span class="faint-label">VILLAGE FACTION</span><h3>好人陣營</h3><p>利用技能、發言與投票找出狼人。</p><div class="feature-number">8 <small>PLAYERS</small></div></div></div>
 <div class="footer-proof">{proof('board_composition')}</div></section>
<section class="slide" id="slide-3" data-title="陣營配置" aria-label="簡報第3頁"><div class="slide-intro"><div class="eyebrow">02 / THE BOARD</div><h2>12 人，<span class="accent">三種身分群</span>。</h2><p class="lead">本課程固定「狼王守衛局」，避免混用不同板子的技能與勝負條件。</p></div>
 <div class="composition"><div class="comp-card"><div class="comp-icon">🐺</div><div class="comp-count">04</div><h3>狼人陣營</h3><p>3 普通狼人＋1 狼王</p></div><div class="comp-card"><div class="comp-icon">🔮</div><div class="comp-count">04</div><h3>神職</h3><p>預言家／女巫／獵人／守衛</p></div><div class="comp-card"><div class="comp-icon">🧑‍🌾</div><div class="comp-count">04</div><h3>平民</h3><p>無夜間技能，依靠推理</p></div></div>
 <div class="bottom-note">主持人不在 12 位玩家之內，負責引導技能與宣告結果。 {proof('board_composition')}</div></section>
<section class="slide" id="slide-4" data-title="角色卡" aria-label="簡報第4頁"><div class="slide-intro"><div class="eyebrow">03 / KNOW YOUR ROLE</div><h2>認識每一張<span class="accent">角色牌</span>。</h2><p class="lead">點擊任意卡片查看技能與限制。翻牌後還可以再點一次關閉。</p></div><div class="role-grid" id="roles">{role_markup}</div>
<div class="bottom-note">角色規則來自 {proof('alpha_death_shot')} {proof('witch_potions')} {proof('guard_repeat')}</div></section>
<section class="slide" id="slide-5" data-title="晝夜流程" aria-label="簡報第5頁"><div class="slide-intro"><div class="eyebrow">04 / THE CYCLE</div><h2>當夜幕降臨，<span class="accent">遊戲開始</span>。</h2><p class="lead">每個回合在夜晚與白天之間循環。主持人按順序引導各角色。</p></div>
<div class="timeline"><div class="time-node"><span>01</span><i>🌙</i><h3>天黑</h3><p>守衛、狼人、預言家、女巫等依順序行動</p></div><div class="time-join">→</div><div class="time-node"><span>02</span><i>🌅</i><h3>天亮</h3><p>主持人公布夜間出局名單</p></div><div class="time-join">→</div><div class="time-node"><span>03</span><i>💬</i><h3>討論</h3><p>存活玩家輪流提出理由</p></div><div class="time-join">→</div><div class="time-node"><span>04</span><i>🗳️</i><h3>投票</h3><p>放逐嫌疑最大的人，接著進入下一夜</p></div></div><div class="bottom-note">本板第一夜照常進行夜間結算。 {proof('night_day_loop')} {proof('first_night_attack')}</div></section>
<section class="slide" id="slide-6" data-title="勝利條件" aria-label="簡報第6頁"><div class="slide-intro"><div class="eyebrow">05 / THE WIN CONDITION</div><h2>遊戲要如何<span class="accent">獲勝</span>？</h2><p class="lead">本課程採用「屠邊」規則，不是所有狼人殺遊戲都採同一種勝利條件。</p></div>
<div class="win-grid"><div class="win-card"><span class="big-emoji">✨</span><h3>好人獲勝</h3><p>所有狼人（包含狼王）都出局。</p><div class="win-rule">WOLVES LEFT = 0</div></div><div class="win-card"><span class="big-emoji">🐺</span><h3>狼人獲勝</h3><p>所有神職出局，<strong>或</strong>所有平民出局。</p><div class="win-rule">GODS = 0 <span>OR</span> VILLAGERS = 0</div></div></div><div class="bottom-note">{proof('wolf_victory')}</div></section>
<section class="slide" id="slide-7" data-title="夜晚模擬器" aria-label="簡報第7頁"><div class="slide-intro"><div class="eyebrow">06 / INTERACTIVE SIMULATOR</div><h2>今晚，<span class="accent">誰會活下來</span>？</h2><p class="lead">你是主持人。選擇狼刀、守衛與女巫行動，按「天亮」模擬結算。</p></div>
<div class="sim-layout"><div class="sim-controls"><div class="input-row"><label for="wolfTarget">🐺 狼刀目標</label><select id="wolfTarget"><option value="6">6 號</option><option value="3">3 號</option><option value="9">9 號</option></select></div><div class="input-row"><label for="guardTarget">🛡️ 守衛守護</label><select id="guardTarget"><option value="6">6 號</option><option value="3">3 號</option><option value="9">9 號</option><option value="none">不守</option></select></div><div class="input-row"><label for="previousGuard">⏮ 上晚守護（驗證連守）</label><select id="previousGuard"><option value="none">前一夜無紀錄</option><option value="6">6 號</option><option value="3">3 號</option><option value="9">9 號</option></select></div><div class="input-row"><label for="witchAction">🧪 女巫行動</label><select id="witchAction"><option value="heal">使用解藥救狼刀目標</option><option value="none">不使用藥</option><option value="poison">使用毒藥（毒 9 號）</option></select></div><button class="primary-btn full" type="button" id="runNight">☀️ 天亮，結算行動</button><button class="text-btn small" type="button" id="resetNight">重設示範</button></div>
<div class="sim-output" id="nightOutput" aria-live="polite"><div class="moon-mini">☽</div><span class="faint-label">WAITING FOR DAWN</span><h3>夜晚尚未結束</h3><p>預設情境：6 號同時被狼人、守衛與女巫解藥選中。</p></div></div><div class="bottom-note">{proof('double_save')} {proof('guard_repeat')} {proof('poison_unblockable')}</div></section>
<section class="slide" id="slide-8" data-title="白天討論" aria-label="簡報第8頁"><div class="slide-intro"><div class="eyebrow">07 / THE SOCIAL GAME</div><h2>白天的武器，<span class="accent">是你的推理</span>。</h2><p class="lead">說話、聽證據、判斷矛盾，最後用放逐投票做出選擇。</p></div>
<div class="discussion-layout"><div class="quote-panel"><div class="quote-mark">“</div><p>「我昨天驗到 8 號是狼人，請大家今天集中放逐 8 號。」</p><small>預言家的可能發言示例；真實對局仍需判斷可信度。</small></div><div class="discussion-steps"><div><span>01</span><strong>聽資訊</strong><p>誰提出了可驗證的內容？</p></div><div><span>02</span><strong>對照矛盾</strong><p>是否有互相衝突的說法？</p></div><div><span>03</span><strong>進行投票</strong><p>警長在本板放逐票計 1.5 票。</p></div></div></div><div class="bottom-note">{proof('sheriff_vote')}</div></section>
<section class="slide" id="slide-9" data-title="知識挑戰" aria-label="簡報第9頁"><div class="slide-intro"><div class="eyebrow">08 / CHECK YOUR UNDERSTANDING</div><h2>你準備好<span class="accent">加入遊戲</span>了嗎？</h2><p class="lead">三題情境判斷；提交後立即看分數、解析與引用來源。</p></div>
<form id="quiz" class="quiz-form"><fieldset><legend>Q1. 狼刀 6 號、守衛守 6 號、女巫救 6 號，6 號會？</legend><label><input type="radio" name="q1" value="a"> 存活，雙重保護</label><label><input type="radio" name="q1" value="b"> 死亡，同守同救</label><label><input type="radio" name="q1" value="c"> 隔天無法投票</label></fieldset><fieldset><legend>Q2. 獵人被女巫毒殺，還可以開槍嗎？</legend><label><input type="radio" name="q2" value="a"> 可以</label><label><input type="radio" name="q2" value="b"> 不可以</label></fieldset><fieldset><legend>Q3. 本板的狼人獲勝條件是哪個？</legend><label><input type="radio" name="q3" value="a"> 人數追平好人</label><label><input type="radio" name="q3" value="b"> 所有神職或所有平民出局</label></fieldset><button type="submit" class="primary-btn" id="submitQuiz">提交答案 →</button><div id="quizResult" class="quiz-result" aria-live="polite"></div></form></section>
<section class="slide" id="slide-10" data-title="回顧與來源" aria-label="簡報第10頁"><div class="slide-intro"><div class="eyebrow">09 / YOU ARE READY</div><h2>歡迎加入<span class="accent">夜晚的遊戲</span>。</h2><p class="lead">現在你已經認識陣營、角色能力、晝夜流程和最常見的結算陷阱。</p></div>
<div class="end-card"><div class="end-badge">✓</div><h3>你完成了 Werewolf Academy</h3><p>記得在開局前先統一規則版本，別把不同板子的說明混為一談。</p><div class="end-actions"><a class="primary-btn" href="wiki/index.html">開啟 18 條規則 Wiki ↗</a><button class="text-btn" type="button" id="restartDeck">重新學習 ↻</button></div></div>
<div class="bottom-note">每條規則均可回查原始來源；本課採教學版而非通用官方規則。 {proof('separate_versions')}</div></section>
</main>
<nav class="deck-nav" aria-label="簡報導覽"><button id="prevSlide" type="button" aria-label="上一頁">←</button><div class="nav-progress"><div class="slide-progress" id="progressTrack"><div class="slide-progress-fill" id="progressFill"></div></div><span id="slideName">Welcome</span></div><span class="slide-number"><strong id="slideCurrent">01</strong><span>/ 10</span></span><button id="nextSlide" type="button" aria-label="下一頁">→</button></nav>
</div>
<script id="claim-data" type="application/json">{json.dumps(rule_data, ensure_ascii=False).replace('</','<\\/')}</script><script src="assets/app.js"></script></body></html>'''
    (root / "index.html").write_text(slides_html, encoding="utf-8")

    grouped = {}
    for r in data:
        grouped.setdefault(r["topic"], []).append(r)
    topics_html = []
    for topic, rules in grouped.items():
        cards = []
        for r in rules:
            sourced = ' '.join(f'<a href="{e(sources[s]["url"])}" target="_blank" rel="noopener noreferrer">{e(s)} ↗</a>' for s in r["source_ids"])
            cards.append(f'''<article class="wiki-entry" id="{e(r['id'])}" data-search="{e(r['title']+' '+r['explanation']+' '+topic+' '+r['id'])}"><div class="entry-top"><span class="entry-id">{e(r['id'])}</span><span class="verified">✓ 證據已核對</span></div><h3>{e(r['title'])}</h3><p>{e(r['explanation'])}</p><div class="rule-foot"><span class="scope">版本 WKG12</span><span>來源 {sourced}</span></div></article>''')
        topics_html.append(f'<section class="topic" id="topic-{e(topic)}"><div class="section-heading"><h2>{e(topic)}</h2><span>{len(rules)} 條規則</span></div><div class="wiki-grid">{"".join(cards)}</div></section>')
    sources_html = '\n'.join(f'<div class="source-row"><div class="src-index">{e(s["id"])}</div><div><strong>{e(s["title"])}</strong><p>{e(s["summary"])}</p><small>版本定位：{e(s["scope"])} · {e(s["type"])}</small></div><a class="src-link" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">原始資料 ↗</a></div>' for s in corpus["sources"])
    conflicts = [
        ("狼人如何獲勝？","WKG12：屠邊（神職或平民全滅）","JINRO_BROWSER：狼人數追平好人即可勝利","S04 / S02","S05"),
        ("首夜是否會出局？","WKG12：首夜照常刀人與結算","JINRO_BROWSER：第一夜不淘汰玩家","S03","S05"),
        ("守衛可否連守？","WKG12：不可連續兩晚守同一人","JINRO_BROWSER：可作為遊戲設定選項","S03","S05"),
    ]
    conflicts_html = '\n'.join(f'<div class="conflict-row"><strong>{e(a)}</strong><div class="variant-main">{e(b)} <small>{e(bsrc)}</small></div><div class="variant-other">{e(c)} <small>{e(csrc)}</small></div></div>' for a,b,c,bsrc,csrc in conflicts)
    wiki_html = f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07111f"><meta name="description" content="12 人狼王守衛局規則資料庫，18 條可追溯規則、7 篇來源和版本衝突對照。"><title>Werewolf Wiki｜可追溯狼人殺知識庫</title><link rel="stylesheet" href="../assets/style.css"></head><body class="wiki-page"><div class="wiki-layout"><header class="topbar"><a class="brand" href="../index.html"><span class="brand-mark">☾</span><span>WEREWOLF<span class="brand-accent">/</span>WIKI</span></a><a class="subtle-link" href="../index.html">返回互動簡報 ↗</a></header>
<div class="wiki-hero"><div class="eyebrow">CURATED KNOWLEDGE · SOURCE TRACEABILITY</div><h1>The Werewolf <em>Codex.</em></h1><p>不是把搜尋結果拼在一起，而是把規則拆成可查詢、可追溯、能辨識不同版本的知識節點。</p><div class="wiki-stats"><span><b>07</b> 來源資料</span><span><b>18</b> 核對規則</span><span><b>03</b> 跨版本差異</span></div></div>
<div class="wiki-toolbar"><label class="search"><span>⌕</span><input id="wikiSearch" aria-label="搜尋Wiki" type="search" placeholder="搜尋守衛、同守同救、女巫、C005..." autocomplete="off"></label><span id="wikiCount">顯示 18 條規則</span></div>
<div class="wiki-main"><aside class="wiki-sidebar"><div class="sidebar-title">主題索引</div>{''.join(f'<a href="#topic-{e(t)}">{e(t)} <span>{len(rs)}</span></a>' for t,rs in grouped.items())}<hr><a href="#conflicts">規則版本差異 →</a><a href="#sources">7 篇原始來源 →</a><a href="../docs/graph.md">Graph 文件 ↗</a></aside><div class="wiki-content"><div class="scope-notice"><strong>重要｜版本約定</strong><p>主教學採 WKG12（12 人狼王守衛局）。其他來源的規則若屬不同遊戲版本，僅用來比較，不會直接進入教學判定。</p></div>{''.join(topics_html)}<section class="topic" id="conflicts"><div class="section-heading"><h2>規則版本差異</h2><span>Version conflicts</span></div><div class="conflicts">{conflicts_html}</div></section><section class="topic" id="sources"><div class="section-heading"><h2>資料來源</h2><span>7 sources · reviewed extracts</span></div><div class="source-list">{sources_html}</div><div class="source-disclaimer">資料處理聲明：此頁整合於 2026-11-21 逐頁核對的來源摘要與規則證據，不含原文全文複製。Pipeline 目前讀取人工核對的摘要證據資料（非即時全文爬蟲）；可另外執行 fetch_sources.py 檢查網頁是否可取得。</div></section></div></div></div><script src="../assets/wiki.js"></script></body></html>'''
    (root / "wiki" / "index.html").write_text(wiki_html, encoding="utf-8")
    return {"slides": 10, "claims": len(data), "sources": len(sources)}

if __name__ == "__main__":
    print(build_site(Path(__file__).resolve().parents[1]))
