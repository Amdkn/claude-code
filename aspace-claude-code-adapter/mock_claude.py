#!/usr/bin/env python3
"""Clean-room test double for the aspace-claude-code-adapter contract.

Written from scratch from the public interface specification (contract.json):
the documented `claude` command surface (README, CLAUDE.md, settings
examples, mods/telemetry README of the upstream reference repo).

This is NOT the upstream CLI and shares NO code with it. It implements only
three verbs of the documented surface, locally, with canned answers:

  --help     print the documented flags and modes
  --version  print the adapter version (never the upstream's)
  --status   read a local settings JSON in a scratch directory and report
             which documented settings keys are present, plus the state of
             the documented telemetry switches from the environment.

Zero network: this file imports only sys, json and os, and opens no socket.
"""

import json
import os
import sys

ADAPTER_VERSION = "0.1.0"
CONTRACT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "contract.json")


def load_contract():
    with open(CONTRACT_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_help(contract):
    iface = contract["interface"]
    lines = [
        "aspace-claude-code-adapter (clean-room test double, not the upstream CLI)",
        "",
        "Usage: claude [options] [prompt]",
        "",
        "Documented entry: `claude` (agentic coding tool, terminal).",
        "Permission modes documented (--permission-mode): " + ", ".join(
            iface["permission_modes_documented"]),
        "Slash commands documented: " + ", ".join(
            iface["slash_commands_documented"]),
        "GitHub mentions: " + iface["github_mentions"],
        "",
        "This double implements only: --help, --version, status.",
        "It never invokes the upstream CLI, copies upstream code, or",
        "makes any network call.",
    ]
    print("\n".join(lines))
    return 0


def cmd_version(contract):
    print(f"aspace-claude-code-adapter {ADAPTER_VERSION} "
          f"(clean-room test double, contract {contract['version']})")
    return 0


def cmd_status(contract):
    settings_path = sys.argv[2] if len(sys.argv) > 2 else None
    present = []
    if settings_path and os.path.exists(settings_path):
        with open(settings_path, encoding="utf-8") as fh:
            settings = json.load(fh)
        documented = set(contract["interface"]["settings_keys_documented"])
        present = sorted(documented & set(settings.keys()))
    switches = {}
    for name in contract["interface"]["telemetry"]["switches_documented"]:
        switches[name] = name in os.environ
    print(json.dumps({
        "adapter": "aspace-claude-code-adapter",
        "adapter_version": ADAPTER_VERSION,
        "clean_room": True,
        "network_calls": 0,
        "settings_keys_present": present,
        "telemetry_switches_set": switches,
    }, indent=2, sort_keys=True))
    return 0


def main(argv):
    contract = load_contract()
    if len(argv) < 2:
        print("usage: mock_claude.py (--help | --version | status [settings.json])",
              file=sys.stderr)
        return 2
    verb = argv[1]
    if verb == "--help":
        return cmd_help(contract)
    if verb == "--version":
        return cmd_version(contract)
    if verb == "status":
        return cmd_status(contract)
    print(f"unknown verb: {verb}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
