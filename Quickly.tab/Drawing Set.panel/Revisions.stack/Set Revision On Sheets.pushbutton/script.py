# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Set selected revisions on selected sheets as additional revisions.

Issued revisions are filtered out of the revision picker — only unissued
revisions can be added to a sheet.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Set Revision\nOn Sheets"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027


def _is_unissued(rev):
    return not rev.Issued


revisions = forms.select_revisions(button_name="Select Revisions",
                                   multiple=True,
                                   filterfunc=_is_unissued)
if not revisions:
    script.exit()

sheets = forms.select_sheets(button_name="Set Revision On These Sheets",
                             include_placeholder=True)
if not sheets:
    script.exit()

with revit.Transaction("Set Revision On Sheets"):
    updated_sheets = revit.update.update_sheet_revisions(revisions, sheets)

output = script.get_output()
output.print_md("# Revisions Added")
output.print_md("**Sheets updated: {}**".format(len(updated_sheets) if updated_sheets else 0))
if updated_sheets:
    for s in updated_sheets:
        number = s.SheetNumber
        name = s.Name
        output.print_md("- `{}` — {}".format(number, name))
