# -*- coding: utf-8 -*-
# Author: Tay Othman
"""For every sheet carrying a selected revision, set a chosen sheet text parameter to "X".

Useful for stamping the per-issue column on a project's sheet-index sheet.
The parameter picker filters to sheet text parameters whose name contains
"/" — the office convention for issue-date column headers like "11/25/25".
"""
from pyrevit import revit, DB, forms, script

__title__ = "Push Revisions\nto Index"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027


def _param_filter(p):
    return "/" in p.name


revision = forms.select_revisions(button_name="Select Revision",
                                  multiple=False)
if not revision:
    script.exit()

sheets = list(DB.FilteredElementCollector(revit.doc)
              .OfCategory(DB.BuiltInCategory.OST_Sheets)
              .WhereElementIsNotElementType())
sheets_to_modify = [s for s in sheets
                    if s.GetAllRevisionIds().Contains(revision.Id)]
if not sheets_to_modify:
    forms.alert("No sheets carry the selected revision.",
                title="Nothing To Update",
                exitscript=True)

target_params = forms.select_parameters(
    sheets_to_modify[0],
    title="Select Index Column to Mark",
    filterfunc=_param_filter,
    button_name="Mark With X",
    exclude_readonly=True,
)
if not target_params:
    script.exit()
target_param_name = target_params[0].name

with revit.Transaction("Push Revisions To Index"):
    for sheet in sheets_to_modify:
        param = sheet.LookupParameter(target_param_name)
        if param and not param.IsReadOnly:
            param.Set("X")

output = script.get_output()
output.print_md("# Pushed `{}` Revision to Index".format(revision.Name))
output.print_md("**Set `{}` = 'X' on {} sheet(s):**".format(target_param_name, len(sheets_to_modify)))
for s in sheets_to_modify:
    output.print_md("- `{}` — {}".format(s.SheetNumber, s.Name))
