#!/usr/bin/env python3
"""verify_install.py - Richard OS installer auto-verification (Stage 3).
Checks every major package/subsystem is present + runnable, prints OK/TODO."""
import pathlib, importlib, sys, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
modules = ["kernel","system_services","autonomy","scheduler","auth","voice_engine",
           "persona_engine","mobile_agent","home_agent","hub","sdk","model_orchestrator"]
files = ["ui/index.html","ui/avatar.html","06-data/hub-index.json","06-data/settings.json",
         "scripts/server.py","src-tauri/tauri.conf.json","install/windows/setup.cmd","install/linux/install.sh"]

print("Richard OS — installation self-check")
ok = True
sys.path.insert(0, str(ROOT / "scripts"))
for m in modules:
    try:
        importlib.import_module(m); print("  ✓ module  ", m)
    except Exception as e:
        print("  ✗ module  ", m, "(%s)" % str(e)[:60]); ok = False
for f in files:
    if (ROOT / f).exists(): print("  ✓ file   ", f)
    else: print("  ✗ file   ", f); ok = False
# hub packages count
try:
    from hub import stats as _hs
    r = _hs(); print("  ✓ hub    ", r.get("in_registry"), "packages")
except Exception as e:
    print("  ✗ hub    ", str(e)[:60]); ok = False
print("RESULT:", "ALL OK — Richard OS installed correctly." if ok else "REVIEW the ✗ items above.")
sys.exit(0 if ok else 1)
