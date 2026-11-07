"""Print bounded exact CERN function excerpts for human source review; never execute."""
from __future__ import annotations
import ast
import hashlib

from src.phase7_official_helper_audit import OFFICIAL_URLS, FUNCTIONS, fetch_source


def main():
    content = fetch_source(OFFICIAL_URLS[0])
    tree = ast.parse(content)
    lines = content.splitlines()
    functions = {x.name: x for x in tree.body if isinstance(x, ast.FunctionDef)}
    print("SOURCE_SHA256", hashlib.sha256(content.encode()).hexdigest())
    for name in FUNCTIONS:
        node = functions.get(name)
        if not node:
            print("MISSING", name)
            continue
        print(f"--- {name}: lines {node.lineno}-{node.end_lineno} ---")
        for line_no in range(node.lineno, node.end_lineno + 1):
            print(f"{line_no:04d}: {lines[line_no - 1]}")
        print(f"--- END {name} ---")


if __name__ == "__main__":
    main()
