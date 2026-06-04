# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Detect dimensions whose Value Override text has been replaced with a manual string.

Scope can be the active view or the entire document. Each flagged dimension is listed
with its true displayed value, its override text, and a clickable element link.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Find Dimension\nOverrides"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()

scope = forms.CommandSwitchWindow.show(
    ["Active View", "Entire Document"],
    message="Choose search scope",
)
if not scope:
    script.exit()

if scope == "Active View":
    view = revit.active_view
    collector = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.Dimension)
else:
    collector = DB.FilteredElementCollector(doc).OfClass(DB.Dimension)

dims = list(collector)
overridden = [d for d in dims
              if isinstance(d.ValueOverride, str) and d.ValueOverride.strip()]

output.print_md("# Dimension Overrides — {}".format(scope))
output.print_md("- Dimensions scanned: **{}**".format(len(dims)))
output.print_md("- Overridden: **{}**".format(len(overridden)))

if not overridden:
    output.print_md("\nNothing to report.")
    script.exit()

output.add_style("overridden { background-color: #ff0000; color: #fff; font-weight: bold; padding: 0 4px; }")
output.add_style("truevalue  { background-color: #1e90ff; color: #fff; font-weight: bold; padding: 0 4px; }")

for dim in overridden:
    true_val = dim.ValueString or "—"
    output.print_html(
        "<truevalue>{}</truevalue> &nbsp; → &nbsp; <overridden>{}</overridden> &nbsp; {}"
        .format(true_val, dim.ValueOverride, output.linkify(dim.Id))
    )
