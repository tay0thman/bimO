# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Build a print sheet set from one or more selected revisions.

When multiple revisions are picked, the user is asked whether sheets must
carry ANY or ALL of those revisions to be included.

After the set is created, empty sheets (no model content) are reported so
the user can verify nothing was placeholder-only.
"""
# pylint: disable=import-error,invalid-name
from pyrevit import revit, forms, script

__title__ = "Create Revision\nPrint Set"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

revisions = forms.select_revisions(button_name="Create Sheet Set",
                                   multiple=True)
if not revisions:
    script.exit()

if len(revisions) > 1:
    mode = forms.CommandSwitchWindow.show(
        ["Matching ANY revision", "Matching ALL revisions"],
        message="Which sheets should the set include?",
    )
    if not mode:
        script.exit()
    match_any = mode == "Matching ANY revision"
else:
    match_any = False  # only one revision picked; ANY vs ALL is moot

with revit.Transaction("Create Revision Sheet Set"):
    sheet_set = revit.create.create_revision_sheetset(revisions,
                                                      match_any=match_any)

empty_sheets = [s for s in sheet_set if revit.query.is_sheet_empty(s)]
if empty_sheets:
    print("\nThese sheets are empty (no model content) — likely placeholders:")
    for s in empty_sheets:
        revit.report.print_sheet(s)
