#!/usr/bin/env python3
"""Build a public, source-linked HTML audit report from actual ingest_run.json."""
from pathlib import Path
import html
import json

ROOT=Path(__file__).resolve().parents[1]

def esc(value):
    return html.escape(str(value),quote=True)

def make_report():
    audit=json.loads((ROOT/'logs/ingest_run.json').read_text(encoding='utf-8'))
    rows=[]
    for rec in audit['records']:
        rows.append(f'''<article class="source">
<div class="head"><strong>{esc(rec.get('source_id',rec['file']))} — {esc(rec.get('title','讀取失敗'))}</strong><span class="pill">{esc(rec['status'])}</span></div>
<p><a href="{esc(rec.get('url','#'))}" target="_blank" rel="noopener noreferrer">原始網頁 ↗</a> · <a href="data/source_inputs/{esc(rec['file'])}">匯入的來源筆記</a></p>
<div class="stats"><span>筆記字數 {esc(rec.get('text_characters',0))}</span><span>分段 {esc(rec.get('chunks_created',0))}</span><span>證據 {esc(rec.get('observations_linked',0))}</span></div>
<small>SHA-256 <code>{esc(rec.get('document_sha256','—'))}</code></small></article>''')
    page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Werewolf Academy｜Ingest 紀錄</title><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,"Noto Sans TC",sans-serif;background:#091321;color:#ebeff5;line-height:1.6}}a{{color:#e4c48a;text-decoration:none}}a:hover{{text-decoration:underline}}header,main{{max-width:1050px;margin:auto;padding:24px}}nav{{display:flex;gap:22px;flex-wrap:wrap}}h1{{font-size:clamp(32px,5vw,55px);line-height:1.1;margin:24px 0 8px}}.sub{{color:#aab8c6}}.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:24px 0}}.metric,.source,.notice{{padding:20px;background:#122236;border:1px solid #294058;border-radius:15px}}.metric strong{{font-size:30px;display:block;color:#f0cf91}}.metric small{{color:#aab8c6}}.source{{margin:12px 0}}.head{{display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap}}.pill{{font-size:12px;padding:4px 9px;border-radius:20px;background:#1a493e;color:#c8ebd8}}.stats{{display:flex;gap:20px;flex-wrap:wrap;font-size:14px;color:#c5d1e2}}code{{overflow-wrap:anywhere}}small{{color:#95a8be}}.notice{{background:#1b2837;border-color:#846c46}}pre{{padding:16px;border-radius:12px;background:#07111b;overflow:auto}}footer{{padding:24px 0;color:#aab8c6;font-size:13px}}
</style></head><body><header><nav><a href="index.html">← 教學簡報</a><a href="wiki/index.html">狼人殺 Wiki</a><a href="logs/ingest_run.json">原始 Log</a><a href="docs/graph.md">Graph 說明</a></nav></header><main>
<div class="sub">EVIDENCE-FIRST PIPELINE / SOURCE INGESTION</div><h1>資料匯入檢查紀錄</h1><p class="sub">以下數字由 <code>pipeline/ingest_sources.py</code> 逐篇讀取來源文件後自動產生。</p>
<div class="summary"><div class="metric"><strong>{audit['source_documents_ingested']}</strong><small>匯入的來源筆記數</small></div><div class="metric"><strong>{audit['chunks_indexed']}</strong><small>可索引知識段落</small></div><div class="metric"><strong>{audit['evidence_records_normalized']}</strong><small>來源連結規則證據</small></div><div class="metric"><strong>{audit['status']}</strong><small>至少 5 筆資料驗證</small></div></div>
<section class="notice"><strong>資料範圍聲明</strong><p>本專案確實使用程式匯入七份獨立的公開網頁來源摘記，並執行驗證、分段、索引及來源證據對應。這七份摘記經網頁核對後重新撰寫，並非七個網站的完整 HTML 自動下載。若課堂要求真正的網站全文抓取，需再於可連網環境執行 <code>pipeline/fetch_sources.py</code>，並提供其成功紀錄。</p></section>
<h2>逐篇匯入記錄</h2>{''.join(rows)}<h2>重新執行指令</h2><pre>python pipeline/ingest_sources.py\npython pipeline/graph.py --demo-both</pre>
<p><a href="data/ingested_sources.json">查看知識庫資料 JSON ↗</a></p><p><a href="data/source_chunks.json">查看原創筆記的段落索引 ↗</a></p>
<footer>Generated {esc(audit['finished_at'])} UTC · 檔案雜湊與各來源筆記成功紀錄均保存於 logs/ingest_run.json。</footer></main></body></html>'''
    (ROOT/'ingest_report.html').write_text(page,encoding='utf-8')
    return ROOT/'ingest_report.html'

if __name__=='__main__':
    print(make_report())
