#!/usr/bin/env python3
"""Reproducible Wiki -> lesson graph. Uses curated, source-linked evidence records.

Modes:
  v1: naive first-observation- wins; checks AFTER slide drafting; late repair loop
  v2: board-scoped verification BEFORE drafting, then independent slide QA
No external API key is required. This is a deterministic, inspectable graph baseline,
not a claim that a remote LLM was called in this execution.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOGS = ROOT / "logs"


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class AcademyGraph:
    def __init__(self, mode: str):
        assert mode in ("v1", "v2")
        self.mode = mode
        self.state = {
            "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + mode,
            "mode": mode,
            "board": "WKG12",
            "events": [],
            "attempts": defaultdict(int),
            "decisions": {},
            "conflicts": [],
            "mismatches_first_pass": [],
            "repairs": [],
            "html_checks": [],
        }
        self.handlers = {
            "ingest": self.ingest,
            "parse": self.parse,
            "extract": self.extract,
            "classify": self.classify,
            "evidence_qa": self.evidence_qa,
            "wiki": self.wiki,
            "plan_slides": self.plan_slides,
            "draft_slides": self.draft_slides,
            "content_qa": self.content_qa,
            "repair_draft": self.repair_draft,
            "build_html": self.build_html,
            "html_qa": self.html_qa,
        }

    def event(self, node, outcome, detail, **extras):
        self.state["attempts"][node] += 1
        self.state["events"].append({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "node": node,
            "attempt": self.state["attempts"][node],
            "outcome": outcome,
            "detail": detail,
            **extras,
        })

    def ingest(self):
        corpus = load_json(DATA / "source_evidence.json")
        ids = [x["id"] for x in corpus["sources"]]
        assert len(ids) == len(set(ids)) and len(ids) >= 5
        assert all(s["url"].startswith("https://") for s in corpus["sources"])
        self.state["corpus"] = corpus
        self.event("ingest", "PASS", f"7-source short evidence corpus parsed; {len(corpus['sources'])} distinct sources", source_count=len(ids), mode="reviewed evidence extracts; not live fetch")

    def parse(self):
        srcs = {x["id"] for x in self.state["corpus"]["sources"]}
        ev = self.state["corpus"]["evidence"]
        assert all(x["source"] in srcs for x in ev)
        assert all(x.get("note") and x.get("scope") for x in ev)
        assert all(s in {x["source"] for x in ev} for s in srcs)
        self.event("parse", "PASS", f"Validated {len(ev)} source-linked evidence records", evidence_count=len(ev))

    def extract(self):
        contract = load_json(DATA / "rule_contract.json")
        evidence_by_key = defaultdict(list)
        for ev in self.state["corpus"]["evidence"]:
            evidence_by_key[ev["key"]].append(ev)
        assert all(r["key"] in evidence_by_key for r in contract["rules"])
        self.state["contract"] = contract
        self.state["evidence_by_key"] = evidence_by_key
        self.event("extract", "PASS", f"Normalized {len(contract['rules'])} teachable claims into keys", rule_count=len(contract["rules"]))

    def classify(self):
        """Classifies conflicting observations by board, not by chronological order."""
        results = {}
        variants = []
        for rule in self.state["contract"]["rules"]:
            obs = self.state["evidence_by_key"][rule["key"]]
            in_board = [e for e in obs if e["scope"] == "WKG12"]
            fallback = [e for e in obs if e["scope"] == "GENERAL_LANGRENSHA"]
            relevant = in_board or fallback
            matches = [e for e in relevant if e["value"] == rule["expected"]]
            if not matches:
                raise ValueError(f"No supported claim in target scope: {rule['id']}")
            results[rule["key"]] = {"value": rule["expected"], "evidence_ids": [e["id"] for e in matches], "source_ids": sorted(set(e["source"] for e in matches))}
            others = [e for e in obs if e["value"] != rule["expected"]]
            for e in others:
                variants.append({"claim": rule["id"], "key": rule["key"], "alternative_value": e["value"], "scope": e["scope"], "source": e["source"], "evidence_id": e["id"], "action": "kept as version variant; excluded from target board"})
        self.state["decisions"] = results
        self.state["conflicts"] = variants
        self.event("classify", "PASS", f"Scoped {len(results)} claims to WKG12 and separated {len(variants)} variant observations", version_variants=len(variants))

    def evidence_qa(self):
        errors = []
        for rule in self.state["contract"]["rules"]:
            d = self.state["decisions"].get(rule["key"])
            if not d or not d["source_ids"] or d["value"] != rule["expected"]:
                errors.append(rule["id"])
        if errors:
            self.event("evidence_qa", "FAIL", "Unsourced/incompatible knowledge: " + ", ".join(errors))
            raise ValueError("Evidence validator cannot approve these claims: " + ", ".join(errors))
        self.event("evidence_qa", "PASS", f"All {len(self.state['contract']['rules'])} claims have version-scoped evidence")

    def wiki(self):
        if self.mode == "v1":
            # Deliberate baseline: first observation wins, ignoring version label.
            self.state["decisions"] = {
                rule["key"]: {"value": self.state["evidence_by_key"][rule["key"]][0]["value"],
                               "evidence_ids": [self.state["evidence_by_key"][rule["key"]][0]["id"]],
                               "source_ids": [self.state["evidence_by_key"][rule["key"]][0]["source"]]}
                for rule in self.state["contract"]["rules"]
            }
            self.event("wiki", "WARN", "Naive V1: first evidence per topic was selected WITHOUT checking version")
        else:
            self.event("wiki", "PASS", "Created wiki records from approved version-scoped claims")

    def plan_slides(self):
        ids = {i for r in self.state["contract"]["rules"] for i in r["slides"]}
        assert set([2,3,4,5,6,7,8,9,10]).issubset(ids)
        self.event("plan_slides", "PASS", "Mapped claims to 10 teaching sections (including cover)")

    def draft_slides(self):
        self.state["slide_draft"] = {rule["id"]: {**self.state["decisions"][rule["key"]], "claim_id": rule["id"]}
                                      for rule in self.state["contract"]["rules"]}
        self.event("draft_slides", "PASS", "Drafted page-linked teaching claims from current wiki")

    def content_qa(self):
        errors = []
        for rule in self.state["contract"]["rules"]:
            item = self.state["slide_draft"][rule["id"]]
            if item["value"] != rule["expected"]:
                errors.append({"id": rule["id"], "key": rule["key"], "observed": item["value"], "expected": rule["expected"], "wrong_source_ids": item["source_ids"]})
        if errors:
            if not self.state["mismatches_first_pass"]:
                self.state["mismatches_first_pass"] = errors
            self.event("content_qa", "FAIL", f"{len(errors)} wrong-version claim(s) found after drafting", error_claims=[e["id"] for e in errors])
            return "repair_draft"
        self.event("content_qa", "PASS", "All final slides match approved WKG12 rules and cite evidence")
        return "build_html"

    def repair_draft(self):
        if self.state["attempts"]["repair_draft"] >= 2:
            raise RuntimeError("Repair retry budget exceeded")
        fixes = []
        for rule in self.state["contract"]["rules"]:
            draft = self.state["slide_draft"][rule["id"]]
            if draft["value"] == rule["expected"]:
                continue
            options = self.state["evidence_by_key"][rule["key"]]
            valid = [e for e in options if e["scope"] in ("WKG12", "GENERAL_LANGRENSHA") and e["value"] == rule["expected"]]
            if not valid:
                raise ValueError(f"Cannot repair {rule['id']}")
            updated = {"value": rule["expected"], "source_ids": sorted(set(e["source"] for e in valid)), "evidence_ids": [e["id"] for e in valid], "claim_id": rule["id"]}
            self.state["slide_draft"][rule["id"]] = updated
            self.state["decisions"][rule["key"]] = {k:v for k,v in updated.items() if k != "claim_id"}
            fixes.append(rule["id"])
        self.state["repairs"].extend(fixes)
        self.event("repair_draft", "REPAIRED", f"Rebuilt {len(fixes)} claims from WKG12 evidence", fixed_claims=fixes)

    def build_html(self):
        if self.mode == "v2":
            verified = []
            for rule in self.state["contract"]["rules"]:
                verified.append({**rule, **self.state["decisions"][rule["key"]], "board": "WKG12", "status": "evidence_checked"})
            write_json(DATA / "verified_claims.json", verified)
            sys.path.insert(0, str(ROOT / "pipeline"))
            from build_site import build_site
            build_site(ROOT)
            self.event("build_html", "PASS", "Generated index.html and wiki/index.html from same verified JSON")
        else:
            self.event("build_html", "SKIPPED", "V1 is an ablation/dry-run, never published")

    def html_qa(self):
        if self.mode == "v1":
            self.event("html_qa", "SKIPPED", "No HTML from V1")
            return
        idx = (ROOT / "index.html").read_text(encoding="utf-8")
        wik = (ROOT / "wiki" / "index.html").read_text(encoding="utf-8")
        checks = {
            "slide_anchors_10": all(f'id="slide-{i}"' in idx for i in range(1,11)),
            "role_flip_control": 'id="roles"' in idx and 'class="role-card"' in idx,
            "night_simulator": 'id="wolfTarget"' in idx and 'id="runNight"' in idx,
            "quiz": 'id="quiz"' in idx and 'submitQuiz' in idx,
            "claim_citations": 'C005' in idx and 'S03' in idx,
            "wiki_search": 'id="wikiSearch"' in wik,
            "seven_sources": all(f"{i:03}" in wik for i in range(1,8)),
            "no_missing_template": "{{" not in idx and "{{" not in wik,
        }
        self.state["html_checks"] = [{"name": k, "pass": v} for k, v in checks.items()]
        if not all(checks.values()):
            self.event("html_qa", "FAIL", "Static HTML check(s) failed", checks=checks)
            raise RuntimeError("HTML QA failed")
        self.event("html_qa", "PASS", f"{len(checks)} static HTML checks passed", checks=checks)

    def run(self):
        # Explicit graph edges plus conditional return from content QA.
        edges = {
            "ingest": "parse", "parse": "extract",
            "classify": "evidence_qa", "evidence_qa": "wiki",
            "wiki": "plan_slides", "plan_slides": "draft_slides",
            "draft_slides": "content_qa", "repair_draft": "content_qa",
            "build_html": "html_qa", "html_qa": None,
        }
        node = "ingest"
        transitions = 0
        while node is not None:
            transitions += 1
            if transitions > 40:
                raise RuntimeError("Loop guard exceeded 40 transitions")
            next_node = self.handlers[node]()
            if node == "extract":
                node = "classify" if self.mode == "v2" else "wiki"
            elif node == "content_qa":
                node = next_node
            else:
                node = edges.get(node)
        s = self.state
        summary = {
            "run_id": s["run_id"], "board": s["board"], "mode": s["mode"],
            "ingestion": "7 manually reviewed, paraphrased source evidence sets (not full-text HTTP downloads)",
            "source_count": len(s["corpus"]["sources"]),
            "evidence_record_count": len(s["corpus"]["evidence"]),
            "claim_count": len(s["contract"]["rules"]),
            "alternative_version_evidence": len(s["conflicts"]),
            "first_pass_late_errors": len(s["mismatches_first_pass"]),
            "late_repaired_claims": len(s["repairs"]),
            "content_qa_attempts": s["attempts"]["content_qa"],
            "static_html_qa_passes": sum(x["pass"] for x in s["html_checks"]),
            "result": "PASS (final)" if s["events"][-1]["outcome"] in ("PASS", "SKIPPED") else "CHECK",
            "variant_conflicts": s["conflicts"],
            "first_pass_errors": s["mismatches_first_pass"],
            "repairs": s["repairs"],
            "events": s["events"],
            "html_checks": s["html_checks"],
        }
        write_json(LOGS / f"run_{self.mode}.json", summary)
        return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=["v1", "v2"], default="v2")
    parser.add_argument("--demo-both", action="store_true", help="Run both graphs and save comparison.json")
    args = parser.parse_args()
    if args.demo_both:
        a = AcademyGraph("v1").run()
        b = AcademyGraph("v2").run()
        comp = {"experiment": "Controlled workflow ablation on the same reviewed evidence; V1 is intentionally version-unaware", "date": "2026-11-21", "v1": {k:a[k] for k in ["source_count", "claim_count", "first_pass_late_errors", "late_repaired_claims", "content_qa_attempts"]}, "v2": {k:b[k] for k in ["source_count", "claim_count", "first_pass_late_errors", "late_repaired_claims", "content_qa_attempts", "alternative_version_evidence", "static_html_qa_passes"]}, "conclusion": "Moving rule-scope checking before slide drafting prevents the variant-mixing errors caused by first-evidence selection in this controlled demo; not an estimate of general LLM accuracy."}
        write_json(LOGS / "comparison.json", comp)
        print(json.dumps(comp, ensure_ascii=False, indent=2))
    else:
        result = AcademyGraph(args.version).run()
        print(json.dumps({k:v for k,v in result.items() if k in ["run_id", "source_count", "claim_count", "alternative_version_evidence", "first_pass_late_errors", "late_repaired_claims", "content_qa_attempts", "static_html_qa_passes", "result"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
