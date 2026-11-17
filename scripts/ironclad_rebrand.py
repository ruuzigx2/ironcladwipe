#!/usr/bin/env python3
"""Re-apply Ironclad Wipe branding to user-visible text after merging a new FMD release.

Run from the repository root:  python3 scripts/ironclad_rebrand.py
It only edits the text inside <string>/<item> entries in values*/strings*.xml files anywhere in the project,
never resource names, comments or the licence notice. Prints every change it makes.
"""
import glob
import re
import sys

# Strings that must keep naming the original project (licence / credit notices).
PROTECTED = {"about_gpl_notice"}

REPLACEMENTS = [
    # "Ironclad Wipe (Find My Device)" / "Ironclad Wipe, Find My Device" -> "Ironclad Wipe"
    (re.compile(r"Ironclad Wipe\s*[（(]\s*Find My Device\s*[)）]"), "Ironclad Wipe"),
    (re.compile(r"Ironclad Wipe,\s*Find My Device"), "Ironclad Wipe"),
    (re.compile(r"Find My Device"), "Ironclad Wipe"),
    (re.compile(r"\bFMD Android\b"), "Ironclad Wipe"),
    (re.compile(r"\bFMD\b(?! ?Server)"), "Ironclad Wipe"),
    # Example SMS commands such as "fmd locate" -> "iron locate"
    (re.compile(r"\bfmd(?= [a-z])"), "iron"),
]

ENTRY = re.compile(r'(<(string|item)\b[^>]*>)(.*?)(</\2>)', re.S)
NAME = re.compile(r'name="([^"]+)"')


def rebrand_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    changes = []

    def fix(m):
        open_tag, _, body, close_tag = m.groups()
        name = NAME.search(open_tag)
        if name and name.group(1) in PROTECTED:
            return m.group(0)
        new = body
        for pat, rep in REPLACEMENTS:
            new = pat.sub(rep, new)
        if new != body:
            changes.append((name.group(1) if name else "?", body.strip()[:80], new.strip()[:80]))
        return open_tag + new + close_tag

    out = ENTRY.sub(fix, text)
    if out != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
    return changes


def main():
    total = 0
    paths = glob.glob("**/values*/strings*.xml", recursive=True)
    paths = [p for p in paths if "/build/" not in p and not p.startswith(("build/", ".git/"))]
    for path in sorted(paths):
        for name, old, new in rebrand_file(path):
            total += 1
            print(f"{path} [{name}]: {old!r} -> {new!r}")
    print(f"{total} string(s) rebranded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
