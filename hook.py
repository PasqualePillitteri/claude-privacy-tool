#!/usr/bin/env python3
"""
Claude Privacy Tool - UserPromptSubmit hook for Claude Code.

Reads a JSON event from stdin, extracts the user prompt, pseudonymizes every
PII using OpenAI Privacy Filter (fully local, offline), stores the placeholder
mapping in ~/.claude/privacy-tool/mappings/, and outputs the sanitized prompt.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path.home() / ".claude" / "privacy-tool"
MAPPINGS_DIR = ROOT / "mappings"
LOG_FILE = ROOT / "hook.log"
MODEL_ID = "openai/privacy-filter"


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def load_classifier():
    from transformers import pipeline
    import torch

    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        task="token-classification",
        model=MODEL_ID,
        aggregation_strategy="simple",
        device=device,
    )


def merge_consecutive(entities: list[dict], max_gap: int = 1) -> list[dict]:
    """
    Fix aggregation_strategy="simple" edge case where the last token of a span
    is tagged slightly differently and breaks the entity in two adjacent pieces.
    Merges entities of the same group whose boundaries touch (gap <= max_gap).
    """
    if not entities:
        return []
    sorted_ents = sorted(entities, key=lambda e: e["start"])
    merged: list[dict] = [dict(sorted_ents[0])]
    for ent in sorted_ents[1:]:
        last = merged[-1]
        same_group = ent.get("entity_group") == last.get("entity_group")
        if same_group and ent["start"] - last["end"] <= max_gap:
            last["end"] = ent["end"]
            last["score"] = max(last.get("score", 0), ent.get("score", 0))
        else:
            merged.append(dict(ent))
    return merged


def sanitize(text: str) -> tuple[str, dict[str, str]]:
    classifier = load_classifier()
    raw_entities = classifier(text)
    entities = merge_consecutive(raw_entities, max_gap=1)
    entities = sorted(entities, key=lambda e: e["start"], reverse=True)

    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}
    seen: dict[tuple[str, str], str] = {}

    masked = text
    for ent in entities:
        group = ent["entity_group"].upper()
        start, end = ent["start"], ent["end"]
        original = text[start:end]
        key = (group, original.strip().lower())
        if key in seen:
            placeholder = seen[key]
        else:
            counters[group] = counters.get(group, 0) + 1
            placeholder = f"[{group}_{counters[group]}]"
            seen[key] = placeholder
            mapping[placeholder] = original
        masked = masked[:start] + placeholder + masked[end:]

    return masked, mapping


def save_mapping(session_id: str, mapping: dict[str, str]) -> str:
    MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)
    mapping_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
    path = MAPPINGS_DIR / f"{mapping_id}.json"
    path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(path, 0o600)
    return mapping_id


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        log(f"ERROR decoding stdin: {exc}")
        return 0

    prompt = event.get("prompt") or event.get("user_prompt") or ""
    session_id = event.get("session_id", "default")

    if not prompt.strip():
        return 0

    try:
        masked, mapping = sanitize(prompt)
    except Exception as exc:
        log(f"ERROR sanitize: {exc}")
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"[PrivacyTool WARNING] Sanitization failed: {exc}. Sending original prompt."
            }
        }))
        return 0

    if not mapping:
        log(f"session={session_id} no PII detected, passthrough")
        return 0

    mapping_id = save_mapping(session_id, mapping)
    stats = {}
    for placeholder in mapping:
        cat = placeholder.strip("[]").rsplit("_", 1)[0]
        stats[cat] = stats.get(cat, 0) + 1
    stats_str = ", ".join(f"{k}({v})" for k, v in sorted(stats.items()))
    log(f"session={session_id} sanitized {len(mapping)} entities: {stats_str} mapping_id={mapping_id}")

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "updatedInput": masked,
            "additionalContext": (
                f"[Claude Privacy Tool] User prompt contained PII, automatically pseudonymized. "
                f"Categories redacted: {stats_str}. Mapping ID (local only): {mapping_id}. "
                f"Answer using the placeholders as they appear; they will be automatically "
                f"replaced with the real values before display to the user."
            )
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
