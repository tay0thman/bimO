# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Scan text notes for 4-digit code years (2007–2031) that aren't the project's current code year.

Useful for catching stale code-cycle references (CBC, IBC, ADA, 11B…) before issuance.
"""
import re

from pyrevit import revit, DB, forms, script

__title__ = "Find Code\nSections"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

CODE_YEARS = ["2016", "2019", "2022", "2025", "2028", "2031"]
YEAR_RANGE = range(2007, 2032)
YEAR_RE = re.compile(r"\b(?:" + "|".join(str(y) for y in YEAR_RANGE) + r")\b")

doc = revit.doc
output = script.get_output()

current_year = forms.CommandSwitchWindow.show(
    CODE_YEARS,
    message="What is this project's current code cycle year?",
)
if current_year is None:
    script.exit()

text_notes = list(DB.FilteredElementCollector(doc).OfClass(DB.TextNote))
matches = []  # list of (text_note, year_token, context)
for note in text_notes:
    text = note.Text or ""
    for m in YEAR_RE.finditer(text):
        token = m.group(0)
        if token == current_year:
            continue
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        context = text[start:end].replace("\n", " ").strip()
        matches.append((note, token, context))
        break  # one hit per text note is enough for reporting

output.print_md("# Code-Year Scan — current year `{}`".format(current_year))
output.print_md("- Text notes scanned: **{}**".format(len(text_notes)))
output.print_md("- Notes containing other code years: **{}**".format(len(matches)))

if not matches:
    output.print_md("\nNo stale code-year references found.")
    script.exit()

for note, token, context in matches:
    output.print_md("- **{}** in {} — `…{}…`"
                    .format(token, output.linkify(note.Id), context))
