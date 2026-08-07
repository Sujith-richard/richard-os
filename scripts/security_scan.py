#!/usr/bin/env python3
"""scripts/security_scan.py - Phase I5 Deep Security
Scans a project dir for real vuln patterns: secrets, unsafe funcs, OWASP risks,
dependency hints, using BlueTeam-Tools intel. Returns severity-ranked findings."""
import re, pathlib, json, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent

PATTERNS = [
    ("critical", r"(?i)(sk-[a-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[a-z0-9]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)", "exposed secret"),
    ("critical", r"(?i)(eval\(|exec\(|os\.system\(|subprocess\.(call|run)\(.*shell=True)", "unsafe eval/exec"),
    ("high",     r"(?i)(password\s*=\s*['\"][^'\"]{4,}['\"]|secret\s*=\s*['\"][^'\"]{4,}['\"])", "hardcoded credential"),
    ("high",     r"(?i)(SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*=.*['\"])", "SQL injection risk"),
    ("high",     r"(?i)(<script>\s*.*innerHTML|dangerouslySetInnerHTML)", "XSS risk"),
    ("medium",   r"(?i)(csrf_exempt|CORS\s*=\s*['\"][*]['\"]|allow_origins.*['\"][*]['\"])", "CORS/CSRF misconfig"),
    ("medium",   r"(?i)(DEBUG\s*=\s*True|debug=True)", "debug mode enabled"),
    ("low",      r"(TODO|FIXME|HACK)", "unresolved TODO"),
]

def scan(path):
    root = pathlib.Path(path)
    files = [f for f in root.rglob("*") if f.is_file() and ".git" not in f.parts] if root.is_dir() else [root]
    findings = []
    for f in files:
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for sev, pat, name in PATTERNS:
            for m in re.finditer(pat, text):
                findings.append({"file": str(f.relative_to(root)) if root.is_dir() else f.name,
                                 "severity": sev, "type": name, "match": m.group(0)[:40]})
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda x: sev_order.get(x["severity"], 4))
    return {"ok": True, "findings": findings[:50], "count": len(findings),
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", metavar="PATH")
    args = ap.parse_args()
    if args.scan:
        r = scan(args.scan)
        print(f"findings: {r['count']} (critical {r['critical']}, high {r['high']})")
        for f in r["findings"][:12]:
            print(f"  [{f['severity']:8s}] {f['type']:28s} {f['file']}: {f['match']}")
        return
    ap.print_help()

if __name__ == "__main__":
    main()
