# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Bulk-rename viewports on selected sheets to "<SheetNumber>-<DetailNumber> - <ViewName>".

The office convention drops periods from sheet numbers (so "A1.01" → "A101")
and strips any office-specific prefix tag (anything before a hyphen in the
first 8 characters of the existing view name) — unless the prefix carries
fire-rating language ("HOUR", "HR", "RATED"), in which case it's preserved.

A preview of every old → new name is shown for confirmation before any
viewport is touched.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Detail\nNaming"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc


def _strip_office_prefix(view_name):
    """Strip an office-specific prefix tag (everything up to the first '-' in the leading 8 chars), preserving fire-rating prefixes."""
    if "-" not in view_name[:5]:
        return view_name
    head = view_name[:8]
    if any(token in head for token in ("HOUR", "HR", "RATED")):
        return view_name
    if "-" in head:
        return head.split("-")[-1] + view_name[8:]
    return view_name


def _compose_name(sheet_number, detail_number, clean_view_name):
    return "{}-{} - {}".format(sheet_number, detail_number, clean_view_name)


sheets = forms.select_sheets(title="Select Sheets to Re-name Viewports")
if not sheets:
    script.exit()

renames = []  # list of (view_element, old_name, new_name, clean_view_name)
for sheet in sheets:
    sheet_number_compact = sheet.SheetNumber.replace(".", "")
    for viewport_id in sheet.GetAllViewports():
        viewport = doc.GetElement(viewport_id)
        view = doc.GetElement(viewport.ViewId)
        old_name = viewport.get_Parameter(DB.BuiltInParameter.VIEWPORT_VIEW_NAME).AsString() or ""
        detail_number = viewport.get_Parameter(DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER).AsString() or ""
        clean_name = _strip_office_prefix(old_name)
        new_name = _compose_name(sheet_number_compact, detail_number, clean_name)
        renames.append((view, old_name, new_name, clean_name))

if not renames:
    forms.alert("No viewports found on the selected sheets.",
                title="Nothing To Rename",
                exitscript=True)

preview = "\n".join("{:<40} >>> {}".format(old, new) for _, old, new, _ in renames)
proceed = forms.alert(
    "Preview ({} viewports):\n\n{}\n\nProceed?".format(len(renames), preview),
    title="Detail Naming Preview",
    ok=True, cancel=True,
)
if not proceed:
    script.exit()

with revit.Transaction("Detail Naming"):
    for view, _, new_name, clean_name in renames:
        view_name_param = view.get_Parameter(DB.BuiltInParameter.VIEW_NAME)
        view_desc_param = view.get_Parameter(DB.BuiltInParameter.VIEW_DESCRIPTION)
        if view_name_param and not view_name_param.IsReadOnly:
            view_name_param.Set(new_name)
        if view_desc_param and not view_desc_param.IsReadOnly:
            view_desc_param.Set(clean_name)

forms.toast("Renamed {} viewport(s)".format(len(renames)),
            title="Detail Naming")
