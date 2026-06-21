# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Scan a folder (and all of its subfolders) for PDFs and write a file_contents.csv index.

Each row records the sheet number, sheet name, and the relative subfolder path.
The filename is split into number/name on the first " - " (space-hyphen-space),
falling back to the first bare "-", so sheet numbers that contain hyphens
(e.g. "A-101 - FLOOR PLAN.pdf") parse correctly. The CSV is written as UTF-8
into the scanned folder and opened automatically.
"""
import os
import io

from pyrevit import forms, script

__title__ = "Package\nContents"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027


def _split_number_name(stem):
    """Split '<sheet number> - <sheet name>' into (number, name).

    Prefers the ' - ' separator so hyphenated sheet numbers (A-101) survive;
    falls back to the first bare '-'. Returns None if neither is present.
    """
    if " - " in stem:
        number, name = stem.split(" - ", 1)
        return number.strip(), name.strip()
    if "-" in stem:
        number, _, name = stem.partition("-")
        return number.strip(), name.strip()
    return None


def _csv_cell(value):
    """Minimal RFC-4180 quoting for one field."""
    text = value if value is not None else ""
    if any(ch in text for ch in (",", '"', "\n", "\r")):
        text = '"' + text.replace('"', '""') + '"'
    return text


folder_path = forms.pick_folder()
if not folder_path:
    script.exit()
if not os.path.isdir(folder_path):
    forms.alert("Folder does not exist:\n{}".format(folder_path),
                title="No Such Folder", exitscript=True)

include_main = forms.alert(
    "Include PDFs in the root folder alongside the subfolders?",
    title="Scan Scope", yes=True, no=True,
)

rows = []
warnings = []
for current_dir, _dirs, files in os.walk(folder_path):
    rel = os.path.relpath(current_dir, folder_path)
    is_root = (rel == ".")
    if is_root and not include_main:
        continue
    subfolder = "" if is_root else rel.replace("\\", "/")
    for name in files:
        if not name.lower().endswith(".pdf"):
            continue
        parsed = _split_number_name(os.path.splitext(name)[0])
        if parsed:
            rows.append([parsed[0], parsed[1], subfolder])
        else:
            label = name if is_root else "{}/{}".format(subfolder, name)
            warnings.append("Skipped (no number/name separator): {}".format(label))

rows.sort(key=lambda r: (r[2], r[0]))

csv_path = os.path.join(folder_path, "file_contents.csv")
try:
    with io.open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.write(u",".join(_csv_cell(h) for h in ("SHEET NUMBER", "SHEET NAME", "SUBFOLDER")) + u"\n")
        for row in rows:
            f.write(u",".join(_csv_cell(c) for c in row) + u"\n")
except IOError as ex:
    forms.alert("Could not write file_contents.csv. Is it open in Excel?\n\n{}".format(ex),
                title="Write Failed", exitscript=True)

output = script.get_output()
output.print_md("## Package Contents")
output.print_md("Wrote **{}** row(s) to `{}`".format(len(rows), csv_path))
if warnings:
    output.print_md("**{} skipped:**".format(len(warnings)))
    for w in warnings:
        output.print_md("- {}".format(w))

os.startfile(csv_path)
