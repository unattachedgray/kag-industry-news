#!/usr/bin/env python3
"""Regenerate the README report index, newest-first (months and rows).

Scans reports/**/YYYY-MM-DD-*.md and rewrites everything between
'## Reports' and the closing '---' line. Existing link titles are kept;
new reports get a default title. Usage: python3 scripts/build_index.py
"""
import re, pathlib, datetime
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DEFAULT_TITLE = "immigration & labor market"
LANGS = {"kr": "Korean", "en": "English"}

text = README.read_text(encoding="utf-8")
start = text.index("## Reports")
end = text.index("\n---", start)
section = text[start:end]
titles = dict((p, t) for t, p in re.findall(r"\[([^\]]+)\]\((reports/[^)]+)\)", section))

rows = []
for f in ROOT.glob("reports/**/*.md"):
    m = re.match(r"(\d{4}-\d{2}-\d{2})-.*?(?:-([a-z]{2}))?\.md$", f.name)
    if not m:
        continue
    rel = f.relative_to(ROOT).as_posix()
    rows.append((m.group(1), rel, titles.get(rel, DEFAULT_TITLE), LANGS.get(m.group(2), m.group(2) or "")))

months = defaultdict(list)
for r in rows:
    months[r[0][:7]].append(r)

out = ["## Reports", ""]
for ym in sorted(months, reverse=True):
    name = datetime.date(int(ym[:4]), int(ym[5:]), 1).strftime("%B %Y")
    out += [f"### {name}", "", "| Date | Report | Language |", "|------|--------|----------|"]
    for d, rel, t, lang in sorted(months[ym], key=lambda r: (r[0], r[1]), reverse=True):
        out.append(f"| {d} | [{t}]({rel}) | {lang} |")
    out.append("")
README.write_text(text[:start] + "\n".join(out) + text[end:], encoding="utf-8")
print(f"Indexed {len(rows)} reports in {len(months)} months")
