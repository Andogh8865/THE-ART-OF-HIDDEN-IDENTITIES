#!/usr/bin/env python3
"""Optional real LLM inspection node for the curated wiki.

Example:
  export OPENAI_API_KEY=...
  python pipeline/llm_review.py

Uses a text-only OpenAI-compatible chat completion endpoint. Writes proposals,
never silently replaces the version-scoped, human-reviewed wiki rules.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]

def main():
    key=os.getenv('OPENAI_API_KEY')
    if not key:raise SystemExit('Missing OPENAI_API_KEY. This step is optional and has NOT been run in the packaged demo.')
    rules=json.loads((ROOT/'data'/'verified_claims.json').read_text(encoding='utf-8'))
    evidence=json.loads((ROOT/'data'/'source_evidence.json').read_text(encoding='utf-8'))['evidence']
    # Small grounded excerpts and explicit scope labels.
    items=[{'rule_id':r['id'],'board':r['board'],'claim':r['explanation'],'evidence':[{'id':x['id'],'scope':x['scope'],'claim':x['note']} for x in evidence if x['id'] in r['evidence_ids']]} for r in rules]
    instruction=('你是教學 Wiki 的證據審稿員。逐項檢查 claim 與提供的證據是否一致，只能依據所給證據。'
                '請用 JSON 陣列輸出，每項含 rule_id, support: supported/unclear/contradicted, reason。'
                '若缺資料請標 unclear，切勿自行補寫或把其他版本規則當成此版本。')
    api=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1').rstrip('/')+'/chat/completions'
    model=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
    payload={'model':model,'temperature':0,'messages':[{'role':'system','content':instruction},{'role':'user','content':json.dumps(items,ensure_ascii=False)}]}
    req=Request(api,data=json.dumps(payload).encode('utf-8'),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    with urlopen(req,timeout=90) as resp:result=json.load(resp)
    answer=result['choices'][0]['message']['content']
    out={'at':datetime.now(timezone.utc).isoformat(),'model':model,'review_raw':answer,'used_claim_count':len(rules),'scope':'optional real LLM review; recommendations require human verification'}
    dest=ROOT/'logs'/'llm_review.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved grounded LLM review to',dest)

if __name__=='__main__':main()
