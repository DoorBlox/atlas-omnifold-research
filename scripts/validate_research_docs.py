#!/usr/bin/env python3
"""Fast, dependency-free continuity and immutable-release checks.

This checks documentation integrity and pinned file bytes. It does NOT validate
experimental covariance, physical coverage, citations or manuscript authorship.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CURRENT_MANUSCRIPT = "ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx"
CURRENT_SHA = "e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62"

ACTIVE = [
    "README.md", "AGENTS.md", "CHATGPT_HANDOFF.md",
    "docs/START_HERE_HANDOFF.md", "docs/CURRENT_STATE.md",
    "docs/DOCUMENTATION_PROTOCOL.md", "docs/ARTIFACT_REGISTRY.md",
    "docs/RESEARCH_WORKFLOW.md", "docs/WRITING_WORKFLOW.md",
    "docs/CHATGPT_TOOL_PLAYBOOK.md", "docs/DECISIONS.md",
    "docs/PROJECT_HISTORY.md", "docs/RESEARCH_STATUS.md",
    "docs/MANUSCRIPT_REVIEW.md", "docs/REPORT_REGISTER.md",
    "docs/ISSUE_REGISTER.md", "plans/RESEARCH_PLAN.md",
]
REQUIRED_HISTORY = [
    "docs/HANDOFF_HISTORY.md",
    "docs/START_HERE_PRE_CHATGPT_2026-11-09.md",
    "docs/KTI_EXECUTIVE_SUMMARY_FACTCHECK_2026_11_08.md",
]
EXTERNAL = ("https:", "http:", "mailto:", "data:", "#")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def check_links(path: Path) -> list[str]:
    """Return missing local Markdown targets for an active documentation file."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in LINK.finditer(text):
        url = match.group(1).strip().split(" ", 1)[0].strip('<>"')
        if not url or url.startswith(EXTERNAL):
            continue
        target = unquote(url.split("#", 1)[0])
        if not target or any(x in target for x in ("{", "*")):
            continue
        resolved = path.parent / target
        if not resolved.exists():
            failures.append(f"{path.relative_to(ROOT)} -> {url}")
    return failures


def main() -> int:
    missing = [p for p in ACTIVE + REQUIRED_HISTORY if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit(f"Missing continuity files: {missing}")
    link_errors = []
    for relative in ACTIVE:
        link_errors.extend(check_links(ROOT / relative))
    if link_errors:
        raise SystemExit("Broken local links: " + "; ".join(link_errors[:20]))

    # Ensure old ChatGPT sessions cannot mistake the author-selected document for v0.6.
    for relative in (
        "CHATGPT_HANDOFF.md", "docs/CURRENT_STATE.md",
        "docs/ARTIFACT_REGISTRY.md", "docs/MANUSCRIPT_REVIEW.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if CURRENT_MANUSCRIPT not in text or CURRENT_SHA not in text:
            raise SystemExit(f"Selected manuscript identity absent: {relative}")
    handoff = (ROOT / "CHATGPT_HANDOFF.md").read_text(encoding="utf-8")
    if "G15" not in handoff or "NO-GO" not in handoff:
        raise SystemExit("Scientific G15 boundary missing in handoff")

    manifest_path = ROOT / "results/four-cell-v1/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("G15") != "NO_GO":
        raise SystemExit("Pinned scientific G15 status changed unexpectedly")
    files = manifest.get("files", {})
    if len(files) != 13:
        raise SystemExit(f"Expected 13 frozen release files; got {len(files)}")
    for rel, expected in sorted(files.items()):
        path = manifest_path.parent / rel
        if not path.is_file():
            raise SystemExit(f"Missing frozen release file: {rel}")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            raise SystemExit(f"Frozen release checksum mismatch: {rel}")

    if (ROOT / CURRENT_MANUSCRIPT).exists():
        raise SystemExit("Author-selected private DOCX unexpectedly placed in public repository root")
    print(f"PASS: {len(ACTIVE)} current docs, local links, manuscript identity, 13 pinned release hashes")
    print("BOUNDARY: documentation checks do not prove scientific inference, reviewer approval or citation validity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
