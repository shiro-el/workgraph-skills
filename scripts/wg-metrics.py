#!/usr/bin/env python3
"""Collect workgraph run metrics from traces into the sibling workgraph-metrics repo.

  wg-metrics.py collect --repo <target-repo> [--out DIR] [--since YYYY-MM-DD]
  wg-metrics.py tlx <project-slug|ISSUE-ID> [--scores m,p,t,perf,e,f] [--out DIR]
  wg-metrics.py selftest

Writes numbers, IDs, models and timestamps only; never code, prose or titles.
Sources: gh (PRs, reviews, comments), Linear GraphQL when LINEAR_API_KEY is set,
Claude transcripts (~/.claude/projects) and Codex transcripts (~/.codex/sessions).
"""
import argparse, json, os, re, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT.parent / "workgraph-metrics"
ROLES = "impl pre e2e setup rv judge tdr arch crit explore verify audit close".split()
ISSUE_RE = re.compile(r"(?<![A-Za-z])([A-Za-z]{2,10}-\d+)")
MARKER_RE = re.compile(r"<!--\s*wg:(\w+)\s+(.*?)-->", re.S)
# the user invoking the wg skill: Claude Skill call or slash command, Codex <skill> injection (JSON-escaped newlines)
WG_CALL = re.compile(r'"skill":\s*"(?:workgraph:)?wg"|<command-name>/(?:workgraph:)?wg</command-name>|<skill>(?:\\n|\s)*<name>(?:workgraph:)?wg</name>')
TLX_ITEMS = ["mental", "physical", "temporal", "performance", "effort", "frustration"]


def version():
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def markers(text):
    """[(kind, {key: value})] for every <!-- wg:kind k=v ... --> in text."""
    return [(k, dict(re.findall(r"([\w-]+)=(\S+)", body))) for k, body in MARKER_RE.findall(text or "")]


def parse_label(name):
    """Agent label -> dict(role, subject, round, idx), or None. Lenient for pre-2.8 ad-hoc names."""
    i = name.rfind("wg-")
    if i < 0:
        return None
    tail = name[i:]
    roles = "|".join(ROLES)
    m = re.fullmatch(r"wg-(%s)-([A-Za-z]{2,10}-\d+)(?:-(\d+))?(?:-(\d+))?" % roles, tail, re.I) or         re.fullmatch(r"wg-(%s)-(.+?)(?:-(\d+))?(?:-(\d+))?" % roles, tail, re.I)
    if m:
        subj = m.group(2)
        return {"role": m.group(1).lower(), "subject": subj.upper() if ISSUE_RE.fullmatch(subj) else subj,
                "round": int(m.group(3)) if m.group(3) else None,
                "idx": int(m.group(4)) if m.group(4) else None}
    im = ISSUE_RE.search(tail)  # legacy, e.g. wg-sopo-129-r1-claude1, wg-sopo-129-pre
    rest = tail[im.end():] if im else tail[3:]
    rm = re.search(r"(?:^|-)r(\d+)", rest)
    role = "rv" if rm else "pre" if "pre" in rest else "close" if "close" in tail else "impl" if im else None
    if not role:
        return None
    return {"role": role, "subject": im.group(1).upper() if im else None,
            "round": int(rm.group(1)) if rm else None, "idx": None, "legacy": True}


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def gh_json(args, cwd):
    return json.loads(sh(["gh"] + args, cwd))


def gh_api(path, cwd):
    return [x for page in gh_json(["api", "--paginate", "--slurp", path], cwd) for x in page]


def iso(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00")) if t else None


# ---------- GitHub ----------

def collect_prs(repo, since):
    slug = gh_json(["repo", "view", "--json", "nameWithOwner"], repo)["nameWithOwner"]
    prs = gh_json(["pr", "list", "--state", "all", "--limit", "1000", "--json",
                   "number,headRefName,baseRefName,createdAt,mergedAt,body,author"], repo)
    rows = []
    for pr in prs:
        if since and pr["createdAt"][:10] < since:
            continue
        head, base = pr["headRefName"], pr["baseRefName"]
        im = ISSUE_RE.search(head.split("/", 1)[-1])
        project = head[8:] if head.startswith("project/") else base[8:] if base.startswith("project/") else None
        if not im and not project:
            continue
        n = pr["number"]
        api = "repos/%s/%%s/%d/%%s" % (slug, n)
        reviews, comments, inline, commits = (gh_api(api % path, repo) for path in
                                              [("pulls", "reviews"), ("issues", "comments"), ("pulls", "comments"), ("pulls", "commits")])
        posts = [(r.get("submitted_at"), r["user"], r.get("body") or "") for r in reviews] + \
                [(c["created_at"], c["user"], c.get("body") or "") for c in comments + inline]
        posts.sort(key=lambda p: p[0] or "")
        rv = [m for _, _, b in posts for k, m in markers(b) if k == "review"]
        passes = [(t, re.search(r"Review passed at ([0-9a-f]{7,40})", b)) for t, _, b in posts]
        passes = [(t, m.group(1)) for t, m in passes if m]
        pass_t, pass_sha = passes[-1] if passes else (None, None)
        if not pass_sha and any(m.get("verdict") == "pass" for m in rv):
            pass_sha = [m for m in rv if m.get("verdict") == "pass"][-1].get("sha")
        shas = [c["sha"] for c in commits]
        post_pass = None
        if pass_sha:
            hit = [i for i, s in enumerate(shas) if s.startswith(pass_sha)]
            post_pass = len(shas) - 1 - hit[-1] if hit else None
        final = not base.startswith("project/")
        human = None
        if final and pass_t:
            human = sum(1 for t, u, b in posts if t and t > pass_t and u.get("type") != "Bot"
                        and not u["login"].endswith("[bot]") and not markers(b)
                        and not re.match(r"\s*(Review passed at|## wg-review|\*\*Changes requested)", b))
        am = re.search(r"Author-model:\s*([\w.-]+)(?:[ \t]+([\w.-]+))?", pr["body"] or "")
        num = lambda key: sum(int(m[key]) for m in rv if m.get(key, "").isdigit()) if any(key in m for m in rv) else None
        rows.append({
            "key": "pr-%d" % n, "repo": slug, "pr": n, "issue": im.group(1).upper() if im else None,
            "project": project, "kind": "project-final" if head.startswith("project/") else "final" if final else "intermediate",
            "wg": next((m["wg"] for m in reversed(rv) if "wg" in m), None),
            "created": pr["createdAt"], "merged": pr["mergedAt"],
            "author_model": am.group(1).lower() if am else None, "author_effort": am.group(2) if am and am.group(2) else None,
            "review_rounds": max((int(m["round"]) for m in rv if m.get("round", "").isdigit()), default=None),
            "round1_pass": (rv[0].get("verdict") == "pass") if rv else None,
            "act": num("act"), "consider": num("consider"), "dismissed": num("dismissed"), "unverified": num("unverified"),
            "commits": len(shas), "post_pass_commits": post_pass, "human_comments": human,
        })
    return slug, rows


# ---------- Linear (optional) ----------

LINEAR_Q = """query($id:String!){ issue(id:$id){ estimate labels{nodes{name}}
 comments(first:100){nodes{body}}
 history(first:100){nodes{createdAt toState{type} addedLabels{name}}} } }"""


def linear_issue(ident, key):
    req = urllib.request.Request("https://api.linear.app/graphql",
                                 json.dumps({"query": LINEAR_Q, "variables": {"id": ident}}).encode(),
                                 {"Content-Type": "application/json", "Authorization": key})
    issue = json.load(urllib.request.urlopen(req, timeout=30)).get("data", {}).get("issue")
    if not issue:
        return {}
    ms = [(k, m) for c in issue["comments"]["nodes"] for k, m in markers(c["body"])]
    hist = sorted(issue["history"]["nodes"], key=lambda h: h["createdAt"])
    state_at = lambda typ: next((h["createdAt"] for h in hist if (h.get("toState") or {}).get("type") == typ), None)
    est = [m for k, m in ms if k == "estimate"]
    prepr = [int(m["round"]) for k, m in ms if k == "prepr" and m.get("round", "").isdigit()]
    names = {l["name"] for l in issue["labels"]["nodes"]} | {l["name"] for h in hist for l in h.get("addedLabels") or []}
    return {"estimate": issue["estimate"], "estimate_proposed": int(est[-1]["proposed"]) if est and est[-1].get("proposed", "").isdigit() else None,
            "started": state_at("started"), "completed": state_at("completed"),
            "needs_human": "needs-human" in names, "prepr_rounds": max(prepr, default=None),
            "contention": sum(int(m["contention"]) for k, m in ms if k == "metrics" and m.get("contention", "").isdigit()) if any(k == "metrics" for k, _ in ms) else None}


# ---------- transcripts ----------

def claude_dirname(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def scan_claude(path, label, source_key):
    seen, row = set(), {"key": source_key, "source": "claude", **label, "model": None, "input": 0, "cache_read": 0,
                        "cache_write": 0, "output": 0, "start": None, "end": None, "tool_errors": 0, "compactions": 0}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t = e.get("timestamp")
            if t:
                row["start"] = min(row["start"] or t, t); row["end"] = max(row["end"] or t, t)
            if e.get("subtype") == "compact_boundary":
                row["compactions"] += 1
            msg = e.get("message") if isinstance(e.get("message"), dict) else {}
            if e.get("type") == "user" and isinstance(msg.get("content"), list):
                row["tool_errors"] += sum(1 for c in msg["content"] if isinstance(c, dict) and c.get("is_error"))
            u = msg.get("usage")
            if e.get("type") == "assistant" and u and msg.get("id") not in seen:
                seen.add(msg.get("id"))
                row["model"] = msg.get("model") or row["model"]
                row["input"] += u.get("input_tokens", 0); row["output"] += u.get("output_tokens", 0)
                row["cache_read"] += u.get("cache_read_input_tokens", 0); row["cache_write"] += u.get("cache_creation_input_tokens", 0)
    return row


def collect_claude(repo, teams):
    base, prefix, rows = Path.home() / ".claude" / "projects", claude_dirname(repo).lower(), []
    for d in base.glob("*") if base.exists() else []:
        in_repo = d.name.lower().startswith(prefix)
        dir_label = parse_label(d.name)
        for s in d.glob("*.jsonl"):
            label = dir_label if dir_label and (in_repo or (dir_label["subject"] or "").split("-")[0] in teams) else None
            if not label and in_repo and WG_CALL.search(s.read_text(encoding="utf-8", errors="replace")):
                label = {"role": "coordinator", "subject": None, "round": None, "idx": None}
            if label:
                rows.append(scan_claude(s, label, "claude-" + s.stem))
            if not (in_repo or label):
                continue
            for meta in (d / s.stem / "subagents").glob("*.meta.json"):
                sub = parse_label(json.loads(meta.read_text(encoding="utf-8")).get("description", ""))
                tr = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
                if sub and tr.exists():
                    rows.append(scan_claude(tr, sub, "claude-" + tr.stem))
    return rows


def collect_codex(repo, teams):
    base, rows = Path.home() / ".codex" / "sessions", []
    norm = lambda p: re.sub(r"^/mnt/([a-z])/", r"\1:/", p.replace("\\", "/"), flags=re.I).lower()
    repo_n = norm(str(repo))
    for f in base.rglob("rollout-*.jsonl") if base.exists() else []:
        row = {"key": "codex-" + f.stem[-36:], "source": "codex", "model": None, "effort": None, "input": 0, "cache_read": 0,
               "cache_write": 0, "output": 0, "start": None, "end": None}
        cwd, label, coord = None, None, False
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                t, p = e.get("timestamp"), e.get("payload") or {}
                if t:
                    row["start"] = min(row["start"] or t, t); row["end"] = max(row["end"] or t, t)
                if e.get("type") == "session_meta":
                    cwd = p.get("cwd") or ""
                    label = parse_label(Path(cwd).name)
                elif e.get("type") == "turn_context":
                    row["model"] = p.get("model") or row["model"]; row["effort"] = p.get("effort") or row["effort"]
                elif p.get("type") == "token_count" and p.get("info"):
                    u = p["info"]["total_token_usage"]  # cumulative
                    row.update(input=u.get("input_tokens", 0) - u.get("cached_input_tokens", 0), cache_read=u.get("cached_input_tokens", 0),
                               cache_write=u.get("cache_write_input_tokens", 0), output=u.get("output_tokens", 0))
                elif not coord and cwd and norm(cwd) == repo_n and WG_CALL.search(line):
                    coord = True
        in_repo = bool(cwd) and norm(cwd).startswith(repo_n)
        if label and (in_repo or (label["subject"] or "").split("-")[0] in teams):
            rows.append({**row, **label})
        elif coord:
            rows.append({**row, "role": "coordinator", "subject": None, "round": None, "idx": None})
    return rows


# ---------- storage ----------

def merge_jsonl(path, rows):
    """Upsert by key; keep records whose source has since disappeared (Claude prunes old transcripts)."""
    old = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line); old[r["key"]] = r
    old.update({r["key"]: r for r in rows})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in old.values()), encoding="utf-8")
    return list(old.values())


def summary(issues, agents):
    tok = {}
    for a in agents:
        if a.get("subject"):
            tok[a["subject"]] = tok.get(a["subject"], 0) + a["input"] + a["cache_read"] + a["cache_write"] + a["output"]
    cols = ["issue", "pr", "kind", "wg", "estimate", "review_rounds", "act", "consider", "dismissed", "post_pass_commits", "human_comments", "Mtok", "hours"]
    print("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
    for r in sorted(issues, key=lambda r: r["pr"]):
        start = iso(r.get("started") or r["created"]); end = iso(r["merged"])
        hours = round((end - start).total_seconds() / 3600, 1) if start and end else None
        mt = round(tok.get(r["issue"], 0) / 1e6, 2) if r["issue"] in tok else None
        vals = [r.get(c) for c in cols[:-2]] + [mt, hours]
        print("| " + " | ".join("" if v is None else str(v) for v in vals) + " |")
    total = sum(a["input"] + a["cache_read"] + a["cache_write"] + a["output"] for a in agents)
    print("\nPRs: %d, agent transcripts: %d, total Mtok: %.2f" % (len(issues), len(agents), total / 1e6))


def cmd_collect(a):
    repo = Path(a.repo).resolve()
    slug, issues = collect_prs(repo, a.since)
    key = os.environ.get("LINEAR_API_KEY")
    if key:
        for r in issues:
            if r["issue"]:
                try:
                    r.update(linear_issue(r["issue"], key))
                except Exception as ex:  # one bad issue should not lose the rest
                    print("linear %s: %s" % (r["issue"], ex), file=sys.stderr)
    else:
        print("LINEAR_API_KEY not set: skipping estimates, status times, prepr and metrics markers", file=sys.stderr)
    teams = {r["issue"].split("-")[0] for r in issues if r["issue"]}
    agents = collect_claude(repo, teams) + collect_codex(repo, teams)
    for r in agents:
        r["repo"] = slug
    d = Path(a.out) / "data" / slug.replace("/", "__")
    issues = merge_jsonl(d / "issues.jsonl", issues)
    agents = merge_jsonl(d / "agents.jsonl", agents)
    summary(issues, agents)
    print("\nwrote %s" % d, file=sys.stderr)


def cmd_tlx(a):
    if a.scores:
        vals = [s.strip() for s in a.scores.split(",")]
    else:
        print("NASA-TLX, 0-100 (performance: 0 = perfect, 100 = failure)")
        vals = [input("%s: " % i) for i in TLX_ITEMS]
    if len(vals) != 6 or not all(v.isdigit() and 0 <= int(v) <= 100 for v in vals):
        sys.exit("need six integers 0-100: " + ",".join(TLX_ITEMS))
    scores = dict(zip(TLX_ITEMS, map(int, vals)))
    row = {"key": "tlx-%s-%s" % (a.subject, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")),
           "subject": a.subject, "wg": version(), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           **scores, "raw_tlx": round(sum(scores.values()) / 6, 1)}
    merge_jsonl(Path(a.out) / "data" / "tlx.jsonl", [row])
    print("raw TLX %.1f saved" % row["raw_tlx"])


def cmd_selftest(_):
    assert parse_label("wg-rv-SOPO-158-2-3") == {"role": "rv", "subject": "SOPO-158", "round": 2, "idx": 3}
    assert parse_label("wg-impl-sopo-12") == {"role": "impl", "subject": "SOPO-12", "round": None, "idx": None}
    assert parse_label("wg-audit-checkout-revamp-1")["subject"] == "checkout-revamp"
    assert parse_label("D--Github-x--claude-worktrees-wg-sopo-129-r1-claude1")["role"] == "rv"
    assert parse_label("D--Github-x--claude-worktrees-wg-sopo-129-pre")["subject"] == "SOPO-129"
    assert parse_label("ACI 관점 리뷰") is None
    assert WG_CALL.search(r'"text":"<skill>\n<name>workgraph:wg</name>') and not WG_CALL.search("Use for $wg in Codex")
    assert markers("x <!-- wg:review wg=2.8.0 sha=ab round=2 act=1 -->")[0] == ("review", {"wg": "2.8.0", "sha": "ab", "round": "2", "act": "1"})
    print("ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect"); c.add_argument("--repo", required=True); c.add_argument("--since"); c.set_defaults(f=cmd_collect)
    t = sub.add_parser("tlx"); t.add_argument("subject"); t.add_argument("--scores"); t.set_defaults(f=cmd_tlx)
    sub.add_parser("selftest").set_defaults(f=cmd_selftest)
    for s in (c, t):
        s.add_argument("--out", default=str(DEFAULT_OUT))
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
