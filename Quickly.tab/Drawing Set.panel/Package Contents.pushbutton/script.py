# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Scan a folder (and optionally its subfolders) for PDFs and write a file_contents.csv index.

Each row records the sheet number, sheet name (split on the first "-" in the
filename), and the subfolder name if any. The CSV is saved into the folder
that was scanned and opened automatically.
"""
import os
import csv

from pyrevit import forms, script

__title__ = "Package\nContents"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027


def _pdf_to_row(filename, subfolder_name=""):
    """Split <sheet number>-<sheet name>.pdf into [number, name, subfolder]. Returns None on bad format."""
    stem, ext = os.path.splitext(filename)
    if ext.lower() != ".pdf" or "-" not in stem:
        return None
    number, _, name = stem.partition("-")
    return [number.strip(), name.strip(), subfolder_name]


folder_path = forms.pick_folder()
if not folder_path:
    script.exit()
if not os.path.isdir(folder_path):
    forms.alert("Folder does not exist:\n{}".format(folder_path),
                title="No Such Folder",
                exitscript=True)

include_main = forms.alert(
    "Include PDFs in the root folder alongside the subfolders?",
    title="Scan Scope",
    yes=True, no=True,
)

rows = []
warnings = []
entries = os.listdir(folder_path)

if include_main:
    for name in entries:
        full = os.path.join(folder_path, name)
        if os.path.isfile(full) and name.lower().endswith(".pdf"):
            row = _pdf_to_row(name)
            if row:
                rows.append(row)
            else:
                warnings.append("Skipped (no hyphen): {}".format(name))

for name in entries:
    sub_path = os.path.join(folder_path, name)
    if not os.path.isdir(sub_path):
        continue
    for sub_name in os.listdir(sub_path):
        if not sub_name.lower().endswith(".pdf"):
            continue
        row = _pdf_to_row(sub_name, subfolder_name=name)
        if row:
            rows.append(row)
        else:
            warnings.append("Skipped (no hyphen): {}/{}".format(name, sub_name))

csv_path = os.path.join(folder_path, "file_contents.csv")
try:
    with open(csv_path, "w") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["SHEET NUMBER", "SHEET NAME", "SUBFOLDER"])
        for row in rows:
            writer.writerow(row)
except IOError as ex:
    forms.alert("Could not write file_contents.csv. Is it open in Excel?\n\n{}".format(ex),
                title="Write Failed",
                exitscript=True)

if warnings:
    print("Warnings:")
    for w in warnings:
        print("  " + w)
print("\nWrote {} row(s) to: {}".format(len(rows), csv_path))

os.startfile(csv_path)
