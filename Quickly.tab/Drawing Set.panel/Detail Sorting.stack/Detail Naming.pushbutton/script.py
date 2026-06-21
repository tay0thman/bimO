# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Bulk-rename viewports on selected sheets to "<SheetNumber>-<DetailNumber> - <ViewName>".

The office convention drops periods from sheet numbers (so "A1.01" -> "A101")
and strips a short office-specific prefix tag (anything before a hyphen in the
leading few characters of the existing view name) -- unless that prefix carries
fire-rating language ("HOUR", "HR", "RATED"), in which case it is preserved.

Each view is renamed (its browser name) and its "Title on Sheet" is set to the
clean view name, so the sheet shows the clean title while the browser stays
organised by sheet. Every change is previewed before anything is touched, and
legends (which can live on several sheets) are skipped so they aren't renamed
out from under their other placements.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Detail\nNaming"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()

FIRE_TOKENS = ("HOUR", "HR", "RATED")


def strip_office_prefix(view_name):
    """Drop a short office prefix tag ('AB-...') cleanly, preserving fire-rating tags."""
    head, sep, tail = view_name.partition("-")
    if not sep or len(head) > 4:
        return view_name                 # no hyphen, or prefix too long to be a tag
    if any(tok in head.upper() for tok in FIRE_TOKENS):
        return view_name                 # keep fire-rating prefixes
    return tail.lstrip()


def compose_name(sheet_number, detail_number, clean_view_name):
    return "{}-{} - {}".format(sheet_number, detail_number, clean_view_name)


def param_string(element, bip):
    param = element.get_Parameter(bip)
    return (param.AsString() or "") if param else ""


sheets = forms.select_sheets(title="Select Sheets to Re-name Viewports")
if not sheets:
    script.exit()

renames = []   # (view, old_name, new_name, clean_name)
skipped = []
for sheet in sheets:
    sheet_number_compact = sheet.SheetNumber.replace(".", "")
    for viewport_id in sheet.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        if view is None:
            continue
        if view.ViewType == DB.ViewType.Legend:
            skipped.append("{} (legend — skipped to avoid renaming it on other sheets)"
                           .format(view.Name))
            continue
        old_name = view.Name
        detail_number = param_string(viewport, DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
        clean_name = strip_office_prefix(old_name)
        new_name = compose_name(sheet_number_compact, detail_number, clean_name)
        renames.append((view, old_name, new_name, clean_name))

if not renames:
    forms.alert("No renameable viewports found on the selected sheets.",
                title="Nothing To Rename", exitscript=True)

# Warn up front about target-name collisions inside this batch (VIEW_NAME must be unique).
counts = {}
for _, _, new_name, _ in renames:
    counts[new_name] = counts.get(new_name, 0) + 1
dupes = ["{} (x{})".format(n, c) for n, c in counts.items() if c > 1]

preview = "\n".join("{:<38} >>> {}   [Title on Sheet: {}]".format(old, new, clean)
                    for _, old, new, clean in renames)
message = "Preview ({} viewport(s)) — renames the view and sets its Title on Sheet:\n\n{}".format(
    len(renames), preview)
if dupes:
    message += "\n\nWARNING — duplicate target names (the duplicates will be skipped):\n" + "\n".join(dupes)
message += "\n\nProceed?"

if not forms.alert(message, title="Detail Naming Preview", ok=True, cancel=True):
    script.exit()

renamed = 0
errors = []
used = set()
with revit.Transaction("Detail Naming"):
    for view, old_name, new_name, clean_name in renames:
        if new_name in used:
            errors.append("{} — duplicate target name '{}'".format(old_name, new_name))
            continue
        try:
            name_param = view.get_Parameter(DB.BuiltInParameter.VIEW_NAME)
            desc_param = view.get_Parameter(DB.BuiltInParameter.VIEW_DESCRIPTION)
            if name_param and not name_param.IsReadOnly:
                name_param.Set(new_name)
            if desc_param and not desc_param.IsReadOnly:
                desc_param.Set(clean_name)
            used.add(new_name)
            renamed += 1
            output.print_md("**{}**  ←  {}".format(new_name, old_name))
        except Exception as err:
            errors.append("{} — {}".format(old_name, err))

output.print_md("---")
output.print_md("Renamed **{}** of {} viewport(s).".format(renamed, len(renames)))
if skipped:
    output.print_md("**Skipped {} legend(s):**".format(len(skipped)))
    for line in skipped:
        output.print_md("- {}".format(line))
if errors:
    output.print_md("**{} error(s):**".format(len(errors)))
    for line in errors:
        output.print_md("- {}".format(line))
