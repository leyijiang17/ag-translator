#!/usr/bin/env python3
"""
Helper for ag-translate's incremental-translation manifest.

Deterministic bits (hashing, reading/writing/diffing the manifest JSON) live
here as plain code rather than being reasoned about fresh by the model each
time, so re-runs are reproducible and the hashing scheme used to decide
"did this block change" can't silently drift between sessions.

Usage:
    python3 manifest_tools.py hash < block_source.txt
    python3 manifest_tools.py diff <manifest.json> <blocks.json>
    python3 manifest_tools.py init <manifest.json> --source <src> --target <tgt> \
        --source-lang oscar --target-lang macaulay2

`blocks.json` for the `diff` command is a JSON array of
{"id": "...", "text": "..."} objects representing the *current* segmentation
of the source file, in order. `diff` prints a JSON object classifying each
block as unchanged / changed / new, plus any manifest entries that no longer
correspond to a current block (removed).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def normalize(text: str) -> str:
    """Normalize whitespace so reformatting alone doesn't count as a change.

    Strips trailing whitespace per line and collapses runs of blank lines,
    but does not touch meaningful content (indentation inside a line,
    actual code tokens) since that could hide a real semantic edit.
    """
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    normalized_lines = []
    prev_blank = False
    for line in lines:
        blank = (line == "")
        if blank and prev_blank:
            continue
        normalized_lines.append(line)
        prev_blank = blank
    return "\n".join(normalized_lines)


def block_hash(text: str) -> str:
    digest = hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def cmd_hash(args):
    text = sys.stdin.read()
    print(block_hash(text))


def cmd_init(args):
    manifest = {
        "source_file": args.source,
        "source_language": args.source_lang,
        "target_file": args.target,
        "target_language": args.target_lang,
        "blocks": [],
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Initialized {args.manifest}")


def cmd_diff(args):
    manifest_path = Path(args.manifest)
    blocks_path = Path(args.blocks)

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {"blocks": []}

    current_blocks = json.loads(blocks_path.read_text())

    manifest_by_id = {b["id"]: b for b in manifest.get("blocks", [])}
    current_ids = {b["id"] for b in current_blocks}

    result = {"unchanged": [], "changed": [], "new": [], "removed": []}

    for block in current_blocks:
        bid = block["id"]
        current_hash = block_hash(block["text"])
        prior = manifest_by_id.get(bid)
        if prior is None:
            result["new"].append(bid)
        elif prior.get("source_hash") == current_hash:
            result["unchanged"].append(bid)
        else:
            result["changed"].append(bid)

    for bid in manifest_by_id:
        if bid not in current_ids:
            result["removed"].append(bid)

    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_hash = sub.add_parser("hash", help="Hash a block's source (read from stdin)")
    p_hash.set_defaults(func=cmd_hash)

    p_init = sub.add_parser("init", help="Create a fresh empty manifest")
    p_init.add_argument("manifest")
    p_init.add_argument("--source", required=True)
    p_init.add_argument("--target", required=True)
    p_init.add_argument("--source-lang", required=True, choices=["oscar", "macaulay2"])
    p_init.add_argument("--target-lang", required=True, choices=["oscar", "macaulay2"])
    p_init.set_defaults(func=cmd_init)

    p_diff = sub.add_parser("diff", help="Classify current blocks against a manifest")
    p_diff.add_argument("manifest")
    p_diff.add_argument("blocks")
    p_diff.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
