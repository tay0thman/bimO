# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Categorize every CAD import / link in the project and list each one with a clickable element link.

Three buckets:
- **Linked Model CADs**  — linked, 3D-scope (visible across all views by default).
- **Linked Detail CADs** — linked, view-specific (placed in a single view).
- **Non-Linked CADs**    — embedded imports (no live source file).
"""
from pyrevit import revit, DB, script

__title__ = "Find CAD"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()


def _cad_display_name(cad):
    return cad.get_Parameter(DB.BuiltInParameter.IMPORT_SYMBOL_NAME).AsString() or "<unnamed>"


cad_imports = list(DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance))

model_linked = []
detail_linked = []
embedded = []

for cad in cad_imports:
    if not cad.IsLinked:
        embedded.append(cad)
        continue
    owner_view = doc.GetElement(cad.OwnerViewId)
    if owner_view is None:
        model_linked.append(cad)
    else:
        detail_linked.append(cad)


def _print_group(title, items):
    output.print_md("### {} ({})".format(title, len(items)))
    if not items:
        output.print_md("_None._\n")
        return
    for cad in items:
        output.print_md("- {}  {}".format(output.linkify(cad.Id), _cad_display_name(cad)))
    output.print_md("")


output.print_md("# CAD Inventory")
_print_group("Linked Model CADs", model_linked)
_print_group("Linked Detail CADs", detail_linked)
_print_group("Non-Linked CADs (embedded imports)", embedded)
