#!/usr/bin/env python3
"""loopkit: agents -> loops -> graph -> self-improvement, in one stdlib-only file.

Lives at loop/loopkit.py in each repo. Data it reads and writes (all in loop/):
  graph.json         nodes (agents, human gates, measure steps) and edges
  rubrics/<id>.json  deterministic checks an output must pass before it moves on
  rubrics/<id>.md    judgement rubric the critic agent scores against (not read here)
  runs.jsonl         one line per node run, plus outcome lines that arrive later
  metrics.jsonl      headline business numbers over time (orders, replies, ...)
  experiments.json   A/B tests of prompt variants (champion vs challenger)
  variants/<node>/   challenger instructions an agent appends to its own prompt

Commands (run from the repo root):
  check <rubric> <file|->              deterministic gate; exit 0 = pass
  variant <node>                       which prompt arm this run should use
  log <node> --status pass|fail ...    record a node run, prints run_id
  outcome (--run ID | --ref REF) k=v   attach a later result (reply, views, sale)
  metric k=v [k=v ...]                 append headline numbers
  experiment start|status|decide       manage A/B tests of prompt changes
  graph [--mermaid]                    node stats as JSON or Mermaid
  dashboard OUT.html [LOOPDIR ...]     self-contained HTML graph dashboard
"""
from __future__ import annotations

import argparse
import html
import json
import math
import os
import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOOP = Path(os.environ.get("LOOP_DIR", Path(__file__).resolve().parent))


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # a half-written line never breaks the loop
    return out


def append_jsonl(p: Path, row: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_kv(pairs: list[str]) -> dict:
    out = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"expected key=value, got {p!r}")
        k, v = p.split("=", 1)
        try:
            out[k] = json.loads(v)
        except json.JSONDecodeError:
            out[k] = v
    return out


# --------------------------------------------------------------------------- checks
LINK_RE = re.compile(r"https?://\S+|(?<![@\w])(?:[a-z0-9-]+\.)+(?:co\.uk|com|uk|io|net|org)(?:/\S*)?", re.I)
HASHTAG_RE = re.compile(r"(?<!\w)#\w+")


def fields_of(text: str) -> dict:
    """Split input into named fields. JSON objects map directly; text with a
    leading 'Subject:' line splits into subject/body."""
    t = text.strip()
    if t.startswith("{"):
        try:
            obj = json.loads(t)
            if isinstance(obj, dict):
                flat = {k: v if isinstance(v, str) else json.dumps(v) for k, v in obj.items()}
                flat["all"] = "\n".join(flat.values())
                return flat
        except json.JSONDecodeError:
            pass
    f = {"all": text}
    m = re.match(r"\s*subject:\s*(.*)\n", text, re.I)
    if m:
        f["subject"] = m.group(1).strip()
        f["body"] = text[m.end():].strip()
    else:
        f["body"] = text
    return f


def words(s: str) -> int:
    return len(re.findall(r"[\w'’-]+", s))


def run_check(c: dict, f: dict) -> tuple[bool, str]:
    field = c.get("field", "all")
    s = f.get(field)
    if s is None:
        return False, f"missing field '{field}'"
    t, v = c["type"], c.get("value")
    low = s.lower()
    if t == "max_words":
        n = words(s); return n <= v, f"{n} words (max {v})"
    if t == "min_words":
        n = words(s); return n >= v, f"{n} words (min {v})"
    if t == "max_chars":
        return len(s) <= v, f"{len(s)} chars (max {v})"
    if t == "min_chars":
        return len(s) >= v, f"{len(s)} chars (min {v})"
    if t == "must_include":
        vals = v if isinstance(v, list) else [v]
        miss = [x for x in vals if x.lower() not in low]
        return not miss, ("missing: " + ", ".join(miss)) if miss else "ok"
    if t == "must_include_any":
        return any(x.lower() in low for x in v), "needs one of: " + ", ".join(v)
    if t == "must_not_include":
        vals = v if isinstance(v, list) else [v]
        hit = [x for x in vals if x.lower() in low]
        return not hit, ("found: " + ", ".join(hit)) if hit else "ok"
    if t == "regex":
        return bool(re.search(v, s, re.I | re.M)), f"pattern {v!r}"
    if t == "not_regex":
        m = re.search(v, s, re.I | re.M)
        return not m, f"matched {m.group(0)!r}" if m else "ok"
    if t == "max_links":
        n = len(LINK_RE.findall(s)); return n <= v, f"{n} links (max {v})"
    if t == "hashtags_between":
        n = len(HASHTAG_RE.findall(s)); return v[0] <= n <= v[1], f"{n} hashtags ({v[0]}-{v[1]})"
    if t == "max_sentence_words":
        longest = max((words(x) for x in re.split(r"[.!?](?:\s|$)|\n", s)), default=0)
        return longest <= v, f"longest sentence {longest} words (max {v})"
    raise SystemExit(f"unknown check type {t!r}")


def check(rubric: dict, text: str) -> dict:
    f = fields_of(text)
    results, must_ok, passed = [], True, 0
    for c in rubric.get("checks", []):
        ok, detail = run_check(c, f)
        sev = c.get("severity", "must")
        results.append({"check": c.get("label", c["type"]), "ok": ok, "severity": sev, "detail": detail})
        passed += ok
        if not ok and sev == "must":
            must_ok = False
    total = len(results) or 1
    return {"pass": must_ok, "score": round(passed / total, 3),
            "failures": [r for r in results if not r["ok"]], "results": results}


def load_rubric(name: str) -> dict:
    p = Path(name)
    if not p.suffix:
        p = LOOP / "rubrics" / f"{name}.json"
    return read_json(p, None) or sys.exit(f"rubric not found: {p}")


# ----------------------------------------------------------------------- experiments
def experiments() -> dict:
    return read_json(LOOP / "experiments.json", {"experiments": []})


def active_exp(node: str) -> dict | None:
    for e in experiments()["experiments"]:
        if e["node"] == node and e["status"] == "running":
            return e
    return None


def runs_and_outcomes():
    rows = read_jsonl(LOOP / "runs.jsonl")
    runs = [r for r in rows if r.get("type", "run") == "run"]
    outs = [r for r in rows if r.get("type") == "outcome"]
    return runs, outs


def merged_metrics(run: dict, outs: list[dict]) -> dict:
    m = {}
    for o in outs:
        if o.get("run_id") == run["run_id"] or (o.get("ref") and o.get("ref") == run.get("ref")
                                                  and o.get("node", run["node"]) == run["node"]):
            m.update(o["metrics"])
    return m


def pick_arm(node: str) -> dict:
    e = active_exp(node)
    if not e:
        return {"experiment": None, "arm": "champion", "file": None}
    runs, _ = runs_and_outcomes()
    counts = {a: 0 for a in e["arms"]}
    for r in runs:
        if r.get("experiment") == e["id"] and r.get("arm") in counts:
            counts[r["arm"]] += 1
    low = min(counts.values())
    arm = random.choice([a for a, n in counts.items() if n == low])
    return {"experiment": e["id"], "arm": arm, "file": e["arms"][arm],
            "hypothesis": e.get("hypothesis")}


def arm_values(e: dict) -> dict[str, list[float]]:
    runs, outs = runs_and_outcomes()
    window = timedelta(days=e.get("outcome_window_days", 0))
    vals: dict[str, list[float]] = {a: [] for a in e["arms"]}
    for r in runs:
        if r.get("experiment") != e["id"] or r.get("arm") not in vals or r.get("status") == "skipped":
            continue
        m = merged_metrics(r, outs)
        key = e["metric"]
        if key in m:
            vals[r["arm"]].append(float(m[key]))
        elif key in ("score", "attempts") and r.get(key) is not None:
            vals[r["arm"]].append(float(r[key]))
        elif e.get("metric_type") == "binary" and now() - parse_ts(r["ts"]) >= window:
            vals[r["arm"]].append(0.0)  # outcome window closed with no result -> 0
        # else: still pending, excluded
    return vals


def norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def compare(a: list[float], b: list[float], binary: bool) -> tuple[float, float]:
    """One-sided p-value that b (challenger) > a (champion), and the lift."""
    na, nb = len(a), len(b)
    ma, mb = sum(a) / na, sum(b) / nb
    if binary:
        p = (sum(a) + sum(b)) / (na + nb)
        se = math.sqrt(max(p * (1 - p) * (1 / na + 1 / nb), 1e-12))
    else:
        va = sum((x - ma) ** 2 for x in a) / max(na - 1, 1)
        vb = sum((x - mb) ** 2 for x in b) / max(nb - 1, 1)
        se = math.sqrt(max(va / na + vb / nb, 1e-12))
    z = (mb - ma) / se
    lift = (mb - ma) / ma if ma else (math.inf if mb > 0 else 0.0)
    return norm_sf(z), lift


def decide(e: dict) -> dict:
    v = arm_values(e)
    a, b = v["champion"], v["challenger"]
    out = {"n": {k: len(x) for k, x in v.items()},
           "mean": {k: round(sum(x) / len(x), 4) if x else None for k, x in v.items()}}
    min_n = e.get("min_n", 20)
    if len(a) < min_n or len(b) < min_n:
        out.update(decision="continue", reason=f"need {min_n} per arm")
        return out
    p_better, lift = compare(a, b, e.get("metric_type") == "binary")
    p_worse, _ = compare(b, a, e.get("metric_type") == "binary")
    alpha = e.get("alpha", 0.1)
    out.update(p=round(p_better, 4), lift=round(lift, 4) if math.isfinite(lift) else "inf")
    if p_better < alpha and lift >= e.get("min_lift", 0.0):
        out.update(decision="promote", reason="challenger beats champion")
    elif p_worse < alpha:
        out.update(decision="reject", reason="challenger is worse")
    elif min(len(a), len(b)) >= e.get("max_n", 3 * min_n):
        out.update(decision="reject", reason="no clear win within budget")
    else:
        out.update(decision="continue", reason="not significant yet")
    return out


# --------------------------------------------------------------------------- graph
def load_graph(loop: Path = None) -> dict:
    g = read_json((loop or LOOP) / "graph.json", None)
    if not g:
        sys.exit(f"no graph.json in {loop or LOOP}")
    return g


def node_stats(loop: Path) -> dict:
    rows = read_jsonl(loop / "runs.jsonl")
    runs = [r for r in rows if r.get("type", "run") == "run"]
    stats = {}
    for r in runs:
        s = stats.setdefault(r["node"], {"runs": 0, "pass": 0, "scores": [], "attempts": [], "last": None})
        s["runs"] += 1
        s["pass"] += r.get("status") == "pass"
        if r.get("score") is not None:
            s["scores"].append(r["score"])
        if r.get("attempts") is not None:
            s["attempts"].append(r["attempts"])
        s["last"] = max(s["last"] or r["ts"], r["ts"])
    for s in stats.values():
        s["pass_rate"] = round(s["pass"] / s["runs"], 3) if s["runs"] else None
        s["avg_score"] = round(sum(s["scores"]) / len(s["scores"]), 3) if s["scores"] else None
        s["avg_attempts"] = round(sum(s["attempts"]) / len(s["attempts"]), 2) if s["attempts"] else None
        del s["scores"], s["attempts"]
    return stats


def layout(g: dict) -> dict[str, tuple[int, int]]:
    """Level = longest path from a root over `next` edges. `loop` edges (the
    self-improvement return) are drawn separately and never affect levels.
    Any remaining cycle in `next` is broken by DFS and treated as a loop edge."""
    nodes = [n["id"] for n in g["nodes"]]
    nxt = {n["id"]: [e for e in n.get("next", []) if e in nodes] for n in g["nodes"]}
    state, order, back = {}, [], set()

    def dfs(u):
        state[u] = 1
        for v in nxt[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2
        order.append(u)

    indeg = {n: 0 for n in nodes}
    for u in nodes:
        for v in nxt[u]:
            indeg[v] += 1
    for u in [n for n in nodes if indeg[n] == 0] + nodes:
        if u not in state:
            dfs(u)
    depth = {n: 0 for n in nodes}
    for u in reversed(order):
        for v in nxt[u]:
            if (u, v) not in back:
                depth[v] = max(depth[v], depth[u] + 1)
    for n in g["nodes"]:
        if "level" in n:
            depth[n["id"]] = n["level"]
    slots: dict[int, int] = {}
    pos = {}
    for n in g["nodes"]:
        d = depth[n["id"]]
        pos[n["id"]] = (d, slots.get(d, 0))
        slots[d] = slots.get(d, 0) + 1
    loops = {(n["id"], v) for n in g["nodes"] for v in n.get("loop", []) if v in nodes}
    g["_back"] = back | loops
    g["_width"] = slots
    return pos


def mermaid(g: dict) -> str:
    shape = {"agent": ('["', '"]'), "human": ('{{"', '"}}'), "measure": ('[("', '")]'), "check": ('(["', '"])')}
    lines = ["flowchart LR"]
    for n in g["nodes"]:
        a, b = shape.get(n.get("kind", "agent"), ('["', '"]'))
        lines.append(f'  {n["id"]}{a}{n["label"]}{b}')
    for n in g["nodes"]:
        for v in n.get("next", []):
            lines.append(f'  {n["id"]} --> {v}')
        for v in n.get("loop", []):
            lines.append(f'  {n["id"]} -.->|improves| {v}')
    return "\n".join(lines)


# ----------------------------------------------------------------------- dashboard
KIND = {"agent": ("Agent", "var(--s1)"), "human": ("You approve", "var(--s2)"),
        "measure": ("Measure", "var(--s3)"), "check": ("Check", "var(--s3)")}
NW, NH, HG, VG, PAD, LANE = 168, 58, 18, 30, 12, 44


def svg_graph(g: dict, stats: dict, exps: list[dict]) -> str:
    """Top-to-bottom layout so it reads on a phone. Loop edges run up the right-hand lane."""
    pos = layout(g)
    levels = max(d for d, _ in pos.values()) + 1
    widest = max(g["_width"].values())
    W = PAD * 2 + widest * NW + (widest - 1) * HG + LANE
    H = PAD * 2 + levels * NH + (levels - 1) * VG
    inner = W - LANE
    xy = {}
    for k, (d, i) in pos.items():
        cnt = g["_width"][d]
        x0 = (inner - (cnt * NW + (cnt - 1) * HG)) / 2
        xy[k] = (x0 + i * (NW + HG), PAD + d * (NH + VG))
    running = {e["node"] for e in exps if e["status"] == "running"}
    out = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" style="width:100%;max-width:{W:.0f}px;height:auto" role="img" aria-label="{html.escape(g["name"])} agent graph">',
           '<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
           '<path d="M0,0 L8,4 L0,8 z" fill="var(--axis)"/></marker></defs>']
    edges = [(n["id"], v) for n in g["nodes"] for v in n.get("next", []) + n.get("loop", []) if v in xy]
    for u, v in edges:
        x1, y1 = xy[u]
        x2, y2 = xy[v]
        if (u, v) in g["_back"]:
            lane, r = W - PAD - 10, 10
            sy, ty = y1 + NH / 2, y2 + NH / 2
            up = 1 if ty < sy else -1
            d = (f"M{x1 + NW},{sy} H{lane - r} Q{lane},{sy} {lane},{sy - up * r} "
                 f"V{ty + up * r} Q{lane},{ty} {lane - r},{ty} H{x2 + NW + 2}")
            out.append(f'<path d="{d}" class="edge back" marker-end="url(#ah)"><title>self-improvement loop</title></path>')
        else:
            sx, sy, tx, ty = x1 + NW / 2, y1 + NH, x2 + NW / 2, y2 - 2
            my = (sy + ty) / 2
            out.append(f'<path d="M{sx},{sy} C{sx},{my} {tx},{my} {tx},{ty}" class="edge" marker-end="url(#ah)"/>')
    for n in g["nodes"]:
        x, y = xy[n["id"]]
        kind = n.get("kind", "agent")
        _, col = KIND.get(kind, KIND["agent"])
        s = stats.get(n["id"], {})
        if kind == "human":
            sub = "needs your OK"
        elif s.get("runs"):
            pr = f' · {round(100 * s["pass_rate"])}% pass' if s.get("pass_rate") is not None else ""
            sub = f'{s["runs"]} runs{pr}'
        else:
            sub = "no runs yet"
        tip = [n["label"], n.get("does", "")]
        if s.get("avg_attempts"):
            tip.append(f'avg attempts {s["avg_attempts"]}')
        if s.get("last"):
            tip.append(f'last run {s["last"]}')
        flag = (f'<circle cx="{x + NW - 11}" cy="{y + 11}" r="5" fill="var(--s2)" stroke="var(--panel)" stroke-width="2">'
                '<title>A/B test running</title></circle>') if n["id"] in running else ""
        out.append(
            f'<g class="node" tabindex="0"><title>{html.escape(" — ".join(t for t in tip if t))}</title>'
            f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="10" class="nbox"/>'
            f'<rect x="{x}" y="{y + 10}" width="4" height="{NH - 20}" rx="2" fill="{col}"/>'
            f'<text x="{x + 14}" y="{y + 24}" class="nlabel">{html.escape(n["label"])}</text>'
            f'<text x="{x + 14}" y="{y + 43}" class="nsub">{html.escape(sub)}</text>{flag}</g>')
    out.append("</svg>")
    return "".join(out)


def sparkline(vals: list[float]) -> str:
    if len(vals) < 2:
        return ""
    w, h = 96, 24
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = " ".join(f"{i * w / (len(vals) - 1):.1f},{h - 2 - (v - lo) / rng * (h - 4):.1f}" for i, v in enumerate(vals))
    return f'<svg width="{w}" height="{h}" aria-hidden="true"><polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round"/></svg>'


def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    if isinstance(v, int):
        return f"{v:,}"
    return html.escape(str(v))


def section(loop: Path) -> str:
    g = load_graph(loop)
    stats = node_stats(loop)
    exps = read_json(loop / "experiments.json", {"experiments": []})["experiments"]
    mrows = read_jsonl(loop / "metrics.jsonl")
    series: dict[str, list] = {}
    for r in mrows:
        for k, v in r.get("values", {}).items():
            series.setdefault(k, []).append((r["ts"], v))
    labels = g.get("metric_labels", {})
    tiles = []
    for k in g.get("headline", list(series)):
        pts = series.get(k, [])
        if not pts:
            tiles.append(f'<div class="tile"><div class="tl">{html.escape(labels.get(k, k))}</div><div class="tv muted">–</div><div class="ts">not measured yet</div></div>')
            continue
        last_ts, last = pts[-1]
        nums = [v for _, v in pts if isinstance(v, (int, float))]
        tiles.append(f'<div class="tile"><div class="tl">{html.escape(labels.get(k, k))}</div>'
                     f'<div class="tv">{fmt(last)}</div>{sparkline(nums)}'
                     f'<div class="ts">as of {last_ts[:10]}</div></div>')
    erows = "".join(
        f'<tr><td>{html.escape(e["id"])}</td><td>{html.escape(e["node"])}</td><td>{html.escape(e.get("hypothesis", ""))}</td>'
        f'<td>{html.escape(e["metric"])}</td><td>{html.escape(e["status"])}</td></tr>' for e in exps
    ) or '<tr><td colspan="5" class="muted">No experiments yet. The improver starts one once a node has enough runs.</td></tr>'
    trows = "".join(
        f'<tr><td>{html.escape(n["label"])}</td><td>{KIND.get(n.get("kind", "agent"))[0]}</td>'
        f'<td>{stats.get(n["id"], {}).get("runs", 0)}</td>'
        f'<td>{"" if stats.get(n["id"], {}).get("pass_rate") is None else str(round(100 * stats[n["id"]]["pass_rate"])) + "%"}</td>'
        f'<td>{stats.get(n["id"], {}).get("avg_attempts") or ""}</td>'
        f'<td>{html.escape(n.get("does", ""))}</td></tr>' for n in g["nodes"])
    notes = "".join(f"<li>{html.escape(x)}</li>" for x in g.get("notes", []))
    return f"""
<section>
  <h2>{html.escape(g["name"])}</h2>
  <p class="lede">{html.escape(g.get("goal", ""))}</p>
  <div class="cols"><div class="graph">{svg_graph(g, stats, exps)}</div><div class="side">
  <div class="tiles">{"".join(tiles)}</div>
  <details><summary>Nodes as a table</summary>
    <table><thead><tr><th>Node</th><th>Type</th><th>Runs</th><th>Pass</th><th>Avg attempts</th><th>Job</th></tr></thead><tbody>{trows}</tbody></table>
  </details>
  <h3>Self-improvement experiments</h3>
  <table><thead><tr><th>ID</th><th>Node</th><th>Change being tested</th><th>Judged on</th><th>Status</th></tr></thead><tbody>{erows}</tbody></table>
  {f'<ul class="notes">{notes}</ul>' if notes else ''}
  </div></div>
</section>"""


CSS = """
.viz-root{color-scheme:light;--surface:#fcfcfb;--panel:#ffffff;--text:#0b0b0b;--text2:#52514e;--muted:#8a897f;--axis:#b4b3ab;--line:#e6e5e0;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--surface);color:var(--text);margin:0;padding:24px}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;--surface:#1a1a19;--panel:#222220;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e86;--axis:#5c5b56;--line:#33332f;--s1:#3987e5;--s2:#d95926;--s3:#199e70}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface:#1a1a19;--panel:#222220;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e86;--axis:#5c5b56;--line:#33332f;--s1:#3987e5;--s2:#d95926;--s3:#199e70}
.wrap{max-width:1180px;margin:0 auto}h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:0 0 2px}h3{font-size:15px;margin:22px 0 8px;color:var(--text2)}
.lede{color:var(--text2);margin:0 0 14px}.muted{color:var(--muted)}
section{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:18px 0}
.legend{display:flex;gap:18px;flex-wrap:wrap;color:var(--text2);font-size:13px;margin:8px 0 0}.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-bottom:14px}
.tile{border:1px solid var(--line);border-radius:10px;padding:10px 12px}.tl{font-size:12px;color:var(--text2)}.tv{font-size:24px;font-weight:600;line-height:1.3}.ts{font-size:11px;color:var(--muted)}
.cols{display:grid;grid-template-columns:minmax(0,400px) minmax(0,1fr);gap:28px;align-items:start}@media (max-width:820px){.cols{grid-template-columns:1fr}}
.graph svg{display:block;margin:0 auto}.side{min-width:0}
.edge{fill:none;stroke:var(--axis);stroke-width:2}.edge.back{stroke-dasharray:5 5}
.nbox{fill:var(--panel);stroke:var(--line);stroke-width:1.5}.node:hover .nbox,.node:focus .nbox{stroke:var(--text2)}.node{outline:none}
.nlabel{font-size:13.5px;font-weight:600;fill:var(--text)}.nsub{font-size:12px;fill:var(--text2)}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--text2);font-weight:600}
details{margin-top:10px}summary{cursor:pointer;color:var(--text2);font-size:13.5px}.notes{color:var(--text2);font-size:13.5px;margin:14px 0 0;padding-left:18px}
"""


def dashboard(out: Path, loops: list[Path], title: str) -> None:
    body = "".join(section(p) for p in loops)
    page = f"""<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body class="viz-root"><div class="wrap"><h1>{html.escape(title)}</h1>
<p class="lede">Each box is an agent with one job. Arrows are hand-offs, read top to bottom. The dashed arrow on the right is the self-improvement loop. Tap or hover a box for its job. Generated {iso(now())[:16].replace("T", " ")} UTC.</p>
<div class="legend"><span><i style="background:var(--s1)"></i>Agent</span><span><i style="background:var(--s2)"></i>Needs your approval</span><span><i style="background:var(--s3)"></i>Measures or checks</span><span><svg width="10" height="10"><circle cx="5" cy="5" r="4" fill="var(--s2)"/></svg> A/B test running</span></div>
{body}</div></body></html>"""
    out.write_text(page, encoding="utf-8")


# ---------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(prog="loopkit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check"); p.add_argument("rubric"); p.add_argument("file")
    p = sub.add_parser("variant"); p.add_argument("node")
    p = sub.add_parser("log")
    p.add_argument("node"); p.add_argument("--status", required=True, choices=["pass", "fail", "skipped"])
    p.add_argument("--score", type=float); p.add_argument("--attempts", type=int)
    p.add_argument("--arm", default="champion"); p.add_argument("--experiment")
    p.add_argument("--ref"); p.add_argument("--note"); p.add_argument("meta", nargs="*")
    p = sub.add_parser("outcome")
    p.add_argument("--run"); p.add_argument("--ref"); p.add_argument("--node"); p.add_argument("kv", nargs="+")
    p = sub.add_parser("metric"); p.add_argument("kv", nargs="+")
    p = sub.add_parser("experiment"); es = p.add_subparsers(dest="ecmd", required=True)
    q = es.add_parser("start"); q.add_argument("node"); q.add_argument("variant_file")
    q.add_argument("--metric", required=True); q.add_argument("--type", choices=["binary", "continuous"], default="binary")
    q.add_argument("--hypothesis", required=True); q.add_argument("--min-n", type=int, default=20)
    q.add_argument("--min-lift", type=float, default=0.0); q.add_argument("--alpha", type=float, default=0.1)
    q.add_argument("--window-days", type=int, default=0)
    es.add_parser("status")
    q = es.add_parser("decide"); q.add_argument("id", nargs="?")
    q = es.add_parser("close"); q.add_argument("id"); q.add_argument("result", choices=["promoted", "rejected"])
    p = sub.add_parser("graph"); p.add_argument("--mermaid", action="store_true")
    p = sub.add_parser("dashboard"); p.add_argument("out"); p.add_argument("loops", nargs="*")
    p.add_argument("--title", default="Agent graph")
    a = ap.parse_args(argv)

    if a.cmd == "check":
        text = sys.stdin.read() if a.file == "-" else Path(a.file).read_text(encoding="utf-8")
        res = check(load_rubric(a.rubric), text)
        print(json.dumps({k: res[k] for k in ("pass", "score", "failures")}, indent=2))
        return 0 if res["pass"] else 1

    if a.cmd == "variant":
        print(json.dumps(pick_arm(a.node)))
        return 0

    if a.cmd == "log":
        rid = f"{a.node}-{now():%Y%m%d%H%M%S}-{random.randrange(16**4):04x}"
        row = {"type": "run", "run_id": rid, "ts": iso(now()), "node": a.node, "status": a.status,
               "score": a.score, "attempts": a.attempts, "arm": a.arm, "experiment": a.experiment,
               "ref": a.ref, "note": a.note, "meta": parse_kv(a.meta)}
        append_jsonl(LOOP / "runs.jsonl", {k: v for k, v in row.items() if v not in (None, {}, "")})
        print(rid)
        return 0

    if a.cmd == "outcome":
        if not (a.run or a.ref):
            sys.exit("give --run RUN_ID or --ref REF")
        row = {"type": "outcome", "ts": iso(now()), "run_id": a.run, "ref": a.ref, "node": a.node, "metrics": parse_kv(a.kv)}
        append_jsonl(LOOP / "runs.jsonl", {k: v for k, v in row.items() if v is not None})
        return 0

    if a.cmd == "metric":
        append_jsonl(LOOP / "metrics.jsonl", {"ts": iso(now()), "values": parse_kv(a.kv)})
        return 0

    if a.cmd == "experiment":
        data = experiments()
        if a.ecmd == "start":
            if active_exp(a.node):
                sys.exit(f"{a.node} already has a running experiment; decide it first (one change at a time)")
            if not Path(a.variant_file).exists():
                sys.exit(f"variant file not found: {a.variant_file}")
            eid = f"exp-{len(data['experiments']) + 1:03d}"
            data["experiments"].append({
                "id": eid, "node": a.node, "status": "running", "started": iso(now()),
                "hypothesis": a.hypothesis, "metric": a.metric, "metric_type": a.type,
                "min_n": a.min_n, "min_lift": a.min_lift, "alpha": a.alpha,
                "outcome_window_days": a.window_days,
                "arms": {"champion": None, "challenger": a.variant_file}})
            write_json(LOOP / "experiments.json", data)
            print(eid)
        elif a.ecmd == "status":
            print(json.dumps([{**{k: e[k] for k in ("id", "node", "status", "metric", "hypothesis")},
                               **(decide(e) if e["status"] == "running" else {})} for e in data["experiments"]], indent=2))
        elif a.ecmd == "decide":
            res = []
            for e in data["experiments"]:
                if e["status"] == "running" and (a.id in (None, e["id"])):
                    d = decide(e)
                    e["last_check"] = {"ts": iso(now()), **d}
                    res.append({"id": e["id"], **d})
            write_json(LOOP / "experiments.json", data)
            print(json.dumps(res, indent=2))
        elif a.ecmd == "close":
            for e in data["experiments"]:
                if e["id"] == a.id:
                    e["status"] = a.result
                    e["closed"] = iso(now())
            write_json(LOOP / "experiments.json", data)
        return 0

    if a.cmd == "graph":
        g = load_graph()
        if a.mermaid:
            print(mermaid(g))
        else:
            print(json.dumps({"name": g["name"], "stats": node_stats(LOOP)}, indent=2))
        return 0

    if a.cmd == "dashboard":
        loops = [Path(x) for x in a.loops] or [LOOP]
        dashboard(Path(a.out), loops, a.title)
        print(a.out)
        return 0


if __name__ == "__main__":
    sys.exit(main())
