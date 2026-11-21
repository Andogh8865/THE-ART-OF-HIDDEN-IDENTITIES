#!/usr/bin/env python3
"""Reproducible integrity checks on the real local-note ingest output."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p: json.loads((ROOT/p).read_text(encoding='utf-8'))
audit=read('logs/ingest_run.json')
corpus=read('data/ingested_sources.json')
chunks=read('data/source_chunks.json')
v1=read('logs/run_v1.json')
v2=read('logs/run_v2.json')
checks={
  'ingest_status_pass':audit['status']=='PASS',
  'min_five_sources':audit['source_documents_ingested']>=5,
  'seven_independent_inputs':len(audit['records'])==7 and all((ROOT/'data/source_inputs'/r['file']).exists() for r in audit['records']),
  'all_hashed_inputs_match':all(hashlib.sha256((ROOT/'data/source_inputs'/r['file']).read_bytes()).hexdigest()==r['document_sha256'] for r in audit['records']),
  'source_count_consistency':len(corpus['sources'])==audit['source_documents_ingested'],
  'chunk_count_consistency':len(chunks)==audit['chunks_indexed'],
  'every_source_has_chunks':{x['source_id'] for x in chunks}=={s['id'] for s in corpus['sources']},
  'every_chunk_hash_valid':all(hashlib.sha256(c['text'].encode('utf-8')).hexdigest()==c['sha256'] for c in chunks),
  'all_observations_have_source':all(x['source'] in {s['id'] for s in corpus['sources']} for x in corpus['evidence']),
  'evidence_count_consistency':len(corpus['evidence'])==audit['evidence_records_normalized'],
  'graph_reads_seven_sources':v1['source_count']==v2['source_count']==audit['source_documents_ingested'],
  'graph_v1_detects_three':v1['first_pass_late_errors']==3,
  'graph_v2_detects_zero':v2['first_pass_late_errors']==0,
  'html_report_generated':(ROOT/'ingest_report.html').is_file(),
  'report_links_in_deck': 'ingest_report.html' in (ROOT/'index.html').read_text(encoding='utf-8'),
}
result={'at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'passed':sum(checks.values()),'total':len(checks),'result':'PASS' if all(checks.values()) else 'FAIL','checks':checks}
(ROOT/'logs/ingest_integrity_tests.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if result['result']!='PASS':raise SystemExit(1)
