#!/usr/bin/env python3
"""OPTIONAL online source acquisition audit (runs only on a networked computer).

Fetches source HTML, extracts text for local analysis, writes audit metadata only.
Does not publish or redistribute full article text.
"""
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__();self.items=[];self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','nav','footer'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','nav','footer'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.items.append(data.strip())


def main():
    corpus=json.loads((ROOT/'data'/'source_evidence.json').read_text(encoding='utf-8'))
    reports=[]
    for s in corpus['sources']:
        try:
            req=Request(s['url'],headers={'User-Agent':'Mozilla/5.0 (Educational source review)'})
            with urlopen(req,timeout=12) as resp:
                raw=resp.read(3_000_000)
                status=resp.status
            parser=VisibleText();parser.feed(raw.decode('utf-8','replace'))
            text=' '.join(parser.items)
            reports.append({'id':s['id'],'url':s['url'],'status':status,'bytes_fetched':len(raw),'visible_chars_extracted':len(text),'sha256':hashlib.sha256(raw).hexdigest(),'result':'FETCHED'})
        except Exception as exc:
            reports.append({'id':s['id'],'url':s['url'],'result':'FAILED','error':str(exc)[:180]})
    out={'fetched_at':datetime.now(timezone.utc).isoformat(),'note':'Only metadata/hashes stored; full copyrighted pages not packaged','sources':reports}
    dest=ROOT/'logs'/'fetch_audit.json'
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Wrote',dest, '| fetched',sum(x['result']=='FETCHED' for x in reports),'of',len(reports),'sources')

if __name__=='__main__':main()
