import json, os, subprocess, re, pathlib, statistics, time
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]

def sh(*cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)

def radon_cc():
    out = sh("radon", "cc", "-j", "-s", ".")
    return json.loads(out)

def radon_mi():
    out = sh("radon", "mi", "-j", ".")
    parsed_output = json.loads(out)
    # parsed_output is already a dict like {'file_path': {'mi': score, 'rank': rank}}
    mi_scores = {file_path: data['mi'] for file_path, data in parsed_output.items()}
    return mi_scores

def python_files():
    return [str(p) for p in ROOT.rglob("*.py") if "venv" not in str(p) and ".venv" not in str(p)]

def churn_90d():
    try:
        since = (time.time() - 90*24*3600)
        since_iso = time.strftime("%Y-%m-%d", time.gmtime(since))
        out = sh("git", "log", f"--since={since_iso}", "--name-only", "--pretty=format:")
        counts = defaultdict(int)
        for line in out.splitlines():
            if line.endswith(".py"):
                counts[line] += 1
        return counts
    except Exception:
        return {}

def import_fanin():
    # very rough: count how often a file path appears in 'from x import' / 'import x'
    fans = defaultdict(int)
    rx = re.compile(r"^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", re.M)
    for f in python_files():
        try:
            s = pathlib.Path(f).read_text(encoding="utf-8", errors="ignore")
            for m in rx.finditer(s):
                mod = (m.group(1) or m.group(2) or "").replace(".", "/") + ".py"
                fans[mod] += 1
        except Exception:
            pass
    return fans

def quantiles(numbers):
    if not numbers: return (0,0,0,0,0)
    arr = sorted(numbers)
    def q(p): 
        idx = int(p*(len(arr)-1))
        return arr[idx]
    return tuple(q(p) for p in [0, .25, .5, .75, 1])

def main():
    cc = radon_cc()
    mi = radon_mi()
    churn = churn_90d()
    fanin = import_fanin()

    results = []
    locs = []
    for path, funcs in cc.items():
        max_cc = max((f["complexity"] for f in funcs), default=0)
        avg_cc = statistics.mean([f["complexity"] for f in funcs]) if funcs else 0
        loc = sum(f.get("endline",0) - f.get("lineno",0) + 1 for f in funcs) or 0
        locs.append(loc)
        results.append({
            "file": path,
            "loc": loc,
            "cc_avg": avg_cc,
            "cc_max": max_cc,
            "mi": mi.get(path, 100.0),
            "fanin": fanin.get(path, 0),
            "churn90": churn.get(path, 0),
        })

    # relative risk via z-scores over the repo (no fixed thresholds)
    def z(xs, x):
        if not xs: return 0.0
        m = statistics.mean(xs); sd = statistics.pstdev(xs) or 1.0
        return (x - m) / sd

    xs_loc = [r["loc"] for r in results]
    xs_cc = [r["cc_max"] for r in results]
    xs_fi = [r["fanin"] for r in results]
    xs_ch = [r["churn90"] for r in results]
    xs_mi = [r["mi"] for r in results]

    for r in results:
        risk = (
            max(0,z(xs_loc, r["loc"])) +
            max(0,z(xs_cc, r["cc_max"])) +
            max(0,z(xs_fi, r["fanin"])) +
            max(0,z(xs_ch, r["churn90"])) +
            max(0,-z(xs_mi, r["mi"]))  # lower MI -> higher risk
        )
        r["risk_score"] = round(risk, 3)

    print(json.dumps({
        "repo": ROOT.name,
        "quantiles_loc": quantiles(xs_loc),
        "results": sorted(results, key=lambda r: r["risk_score"], reverse=True)
    }, indent=2))

if __name__ == "__main__":
    main()
