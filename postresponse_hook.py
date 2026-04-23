#!/usr/bin/env python3
"""
Claude Privacy Tool - post-response desanitization hook for Claude Code.

Runs as `Stop` hook. Reads the response from stdin, reverses placeholders back
to the real values using the locally stored mapping, and prints the
reconstructed response on stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path.home() / ".claude" / "privacy-tool"
MAPPINGS_DIR = ROOT / "mappings"


def load_all_mappings_for_session(session_id: str) -> dict[str, str]:
    merged: dict[str, str] = {}
    if not MAPPINGS_DIR.exists():
        return merged
    for path in MAPPINGS_DIR.glob(f"{session_id}_*.json"):
        try:
            merged.update(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return merged


def desanitize(text: str, mapping: dict[str, str]) -> str:
    keys = sorted(mapping.keys(), key=len, reverse=True)
    for placeholder in keys:
        text = text.replace(placeholder, mapping[placeholder])
    return text


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    session_id = event.get("session_id", "default")
    response_text = event.get("response") or event.get("assistant_response") or ""

    if not response_text.strip():
        return 0

    mapping = load_all_mappings_for_session(session_id)
    if not mapping:
        return 0

    restored = desanitize(response_text, mapping)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "updatedResponse": restored
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
