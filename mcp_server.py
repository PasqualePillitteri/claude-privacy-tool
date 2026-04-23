#!/usr/bin/env python3
"""
Claude Privacy Tool - MCP server for Claude Desktop.

Exposes privacy tools via the Model Context Protocol:
  - privacy_sanitize(text, session_id): pseudonymize PII in text
  - privacy_desanitize(text, mapping_id, session_id): reverse placeholders
  - privacy_list_sessions(): list stored sessions
  - privacy_purge_session(session_id): GDPR right-to-erasure

Processing is local. Mappings live in ~/.claude/privacy-tool/mappings/ (0600).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP


ROOT = Path.home() / ".claude" / "privacy-tool"
MAPPINGS_DIR = ROOT / "mappings"
LOG_FILE = ROOT / "mcp.log"
MODEL_ID = "openai/privacy-filter"

_classifier = None


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def get_classifier():
    global _classifier
    if _classifier is None:
        from transformers import pipeline
        import torch

        device = 0 if torch.cuda.is_available() else -1
        _classifier = pipeline(
            task="token-classification",
            model=MODEL_ID,
            aggregation_strategy="simple",
            device=device,
        )
        log(f"Model loaded on {'GPU' if device == 0 else 'CPU'}")
    return _classifier


def _sanitize_core(text: str) -> tuple[str, dict[str, str], dict[str, int]]:
    classifier = get_classifier()
    entities = sorted(classifier(text), key=lambda e: e["start"], reverse=True)

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

    return masked, mapping, counters


def _save_mapping(session_id: str, mapping: dict[str, str]) -> str:
    MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)
    mapping_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
    path = MAPPINGS_DIR / f"{mapping_id}.json"
    path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    path.chmod(0o600)
    return mapping_id


def _load_mapping(mapping_id: str) -> dict[str, str] | None:
    path = MAPPINGS_DIR / f"{mapping_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log(f"ERROR loading mapping {mapping_id}: {exc}")
        return None


def _load_session_mappings(session_id: str) -> dict[str, str]:
    merged: dict[str, str] = {}
    if not MAPPINGS_DIR.exists():
        return merged
    for path in MAPPINGS_DIR.glob(f"{session_id}_*.json"):
        try:
            merged.update(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return merged


mcp = FastMCP("claude-privacy-tool")


@mcp.tool()
def privacy_sanitize(text: str, session_id: str = "default") -> dict:
    """
    Pseudonymize all personal data in the given text.

    Replaces every detected PII (names, addresses, emails, phones, dates,
    account numbers, secrets) with numbered placeholders like
    [PRIVATE_PERSON_1], [ACCOUNT_NUMBER_1]. Originals are stored locally and
    recoverable via privacy_desanitize using the returned mapping_id.

    Args:
        text: Raw text to sanitize.
        session_id: Logical session to group multiple mappings.

    Returns:
        A dict with masked, mapping_id, stats, entity_count.
    """
    if not text.strip():
        return {"masked": text, "mapping_id": None, "stats": {}, "entity_count": 0}
    masked, mapping, counters = _sanitize_core(text)
    if not mapping:
        return {"masked": text, "mapping_id": None, "stats": {}, "entity_count": 0}
    mapping_id = _save_mapping(session_id, mapping)
    log(f"sanitize session={session_id} entities={len(mapping)} mapping_id={mapping_id}")
    return {
        "masked": masked,
        "mapping_id": mapping_id,
        "stats": counters,
        "entity_count": len(mapping),
    }


@mcp.tool()
def privacy_desanitize(text: str, mapping_id: str = "", session_id: str = "default") -> dict:
    """
    Replace placeholders with their original values using a stored mapping.

    Args:
        text: Text containing placeholders produced by privacy_sanitize.
        mapping_id: Specific mapping to use (optional).
        session_id: Session whose mappings should be merged if mapping_id is empty.

    Returns:
        A dict with original, replacements.
    """
    if mapping_id:
        mapping = _load_mapping(mapping_id) or {}
    else:
        mapping = _load_session_mappings(session_id)

    if not mapping:
        return {"original": text, "replacements": 0}

    replacements = 0
    restored = text
    for placeholder in sorted(mapping.keys(), key=len, reverse=True):
        if placeholder in restored:
            restored = restored.replace(placeholder, mapping[placeholder])
            replacements += 1

    log(f"desanitize session={session_id} replacements={replacements}")
    return {"original": restored, "replacements": replacements}


@mcp.tool()
def privacy_list_sessions() -> dict:
    """List all session IDs that currently have stored mappings on disk."""
    if not MAPPINGS_DIR.exists():
        return {"sessions": [], "count": 0}
    sessions = sorted({p.stem.rsplit("_", 1)[0] for p in MAPPINGS_DIR.glob("*.json")})
    return {"sessions": sessions, "count": len(sessions)}


@mcp.tool()
def privacy_purge_session(session_id: str) -> dict:
    """
    Delete all mappings for a given session. Irreversible.

    Use this to comply with GDPR right-to-erasure requests or simply to
    wipe sensitive data after a work session is complete.
    """
    if not MAPPINGS_DIR.exists():
        return {"deleted": 0}
    deleted = 0
    for path in MAPPINGS_DIR.glob(f"{session_id}_*.json"):
        path.unlink()
        deleted += 1
    log(f"purged session={session_id} files={deleted}")
    return {"deleted": deleted}


if __name__ == "__main__":
    mcp.run()
