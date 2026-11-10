#!/usr/bin/env python3
"""Smoke test for the aspace-claude-code-adapter contract (clean-room, D12).

Stdlib only. Checks, against a local scratch directory and a from-scratch
test double (mock_claude.py), never against the upstream CLI or any upstream
code:

  1. contract.json parses and carries the required fields;
  2. mock --help exits 0 and names the documented entry and modes;
  3. mock --version exits 0 and says clean-room;
  4. mock status exits 0, returns valid JSON, reports the documented
     settings keys present in a scratch settings file and the documented
     telemetry switches;
  5. the adapter contains NO network code (no socket / urllib / requests /
     http.client anywhere in its .py files) — zero traffic by construction;
  6. the adapter imports NOTHING from the upstream repo (stdlib only).

Usage: python3 smoke_test.py
Exit 0 = 6/6 checks pass.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "mock_claude.py")
CONTRACT = os.path.join(HERE, "contract.json")

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))


def run(args, env=None):
    merged = dict(os.environ)
    merged.pop("DISABLE_TELEMETRY", None)
    merged.pop("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", None)
    merged.pop("DO_NOT_TRACK", None)
    if env:
        merged.update(env)
    return subprocess.run([sys.executable, MOCK] + args,
                          capture_output=True, text=True, env=merged)


def main():
    # 1. Contract parses and carries the required fields.
    try:
        with open(CONTRACT, encoding="utf-8") as fh:
            contract = json.load(fh)
        ok = (contract.get("clean_room") is True
              and contract["adapter"] == "aspace-claude-code-adapter"
              and contract["upstream"]["frozen_commit"]
              == "0ed94698aa0aeee471465fc9c867c2e8434c4d68"
              and contract["upstream"]["license"] is None
              and "permission_modes_documented" in contract["interface"]
              and "telemetry" in contract["interface"])
        check("contract", ok, "contract.json valide, gel + D12 portés")
    except Exception as exc:  # noqa: BLE001 - smoke test reports, never crashes
        check("contract", False, str(exc))
        contract = {}

    # 2. mock --help.
    res = run(["--help"])
    check("help", res.returncode == 0
          and "claude" in res.stdout
          and "--permission-mode" in res.stdout,
          "entry + modes documentés nommés")

    # 3. mock --version.
    res = run(["--version"])
    check("version", res.returncode == 0
          and "clean-room" in res.stdout
          and "aspace-claude-code-adapter" in res.stdout,
          res.stdout.strip().splitlines()[0] if res.stdout else "vide")

    # 4. mock status with a scratch settings file.
    with tempfile.TemporaryDirectory() as scratch:
        settings_path = os.path.join(scratch, "settings.json")
        with open(settings_path, "w", encoding="utf-8") as fh:
            json.dump({"allowedProviders": ["anthropic"],
                       "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                       "unknownKey": True}, fh)
        res = run(["status", settings_path],
                  env={"DO_NOT_TRACK": "1"})
        try:
            payload = json.loads(res.stdout)
            ok = (res.returncode == 0
                  and payload.get("clean_room") is True
                  and payload.get("network_calls") == 0
                  and payload["settings_keys_present"]
                  == ["CLAUDE_CODE_ENABLE_TELEMETRY", "allowedProviders"]
                  and payload["telemetry_switches_set"].get("DO_NOT_TRACK")
                  is True)
            check("status", ok, "clés documentées détectées, "
                  "DO_NOT_TRACK lu, 0 appel réseau")
        except Exception as exc:  # noqa: BLE001
            check("status", False, f"{exc} — sortie : {res.stdout[:200]!r}")

    # 5. No network code anywhere in the adapter: parse each .py file
    # with ast and collect the root modules actually imported or used.
    # (A word search would trip on this test's own docstrings.)
    import ast
    network_roots = {"socket", "urllib", "requests", "http", "httpx",
                     "aiohttp", "websocket", "ssl"}
    hits = []
    for name in os.listdir(HERE):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(HERE, name), encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in network_roots:
                        hits.append(f"{name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] in network_roots:
                    hits.append(f"{name}: from {node.module} import")
    check("zero-network", not hits,
          "aucun import réseau dans l'adapter" if not hits
          else f"trouvé : {', '.join(hits)}")

    # 6. Stdlib only — no import from the upstream repo.
    imported = set()
    for name in os.listdir(HERE):
        if name.endswith(".py"):
            with open(os.path.join(HERE, name), encoding="utf-8") as fh:
                imported.update(re.findall(r"^(?:import|from)\s+(\w+)",
                                           fh.read(), re.M))
    stdlib = set(sys.stdlib_module_names)
    outside = sorted(m for m in imported if m not in stdlib)
    check("stdlib-only", not outside,
          "imports = stdlib seule" if not outside
          else f"hors stdlib : {', '.join(outside)}")

    failed = [name for name, ok, _ in CHECKS if not ok]
    print(f"\nsmoke claude-code-adapter : "
          f"{len(CHECKS) - len(failed)}/{len(CHECKS)} checks pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
