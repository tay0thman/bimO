# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Detect dimensions whose value has been overridden with manual text.

Scope can be the active view or the entire document. Both single- and
multi-segment dimensions are checked (each segment of a string dimension can
carry its own override); every overridden value is listed with its true
measurement, the override text, and a clickable element link.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Find Dimension\nOverrides"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()


def has_override(value_override):
    return bool(value_override) and value_override.strip() != ""


def iter_values(dim):
    """Yield (true_value_string, override_text) for each segment of a dimension."""
    if dim.NumberOfSegments > 0:          # multi-segment: overrides live on the segments
        for seg in dim.Segments:
            yield seg.ValueString, seg.ValueOverride
    else:                                 # single-segment: value lives on the dimension
        yield dim.ValueString, dim.ValueOverride


scope = forms.CommandSwitchWindow.show(
    ["Active View", "Entire Document"],
    message="Choose search scope",
)
if not scope:
    script.exit()

if scope == "Active View":
    collector = DB.FilteredElementCollector(doc, revit.active_view.Id).OfClass(DB.Dimension)
else:
    collector = DB.FilteredElementCollector(doc).OfClass(DB.Dimension)

dims = list(collector)
flagged = []   # (true_value_string, override_text, dim)
for dim in dims:
    for true_val, override in iter_values(dim):
        if has_override(override):
            flagged.append((true_val or "—", override, dim))

output.print_md("# Dimension Overrides — {}".format(scope))
output.print_md("- Dimensions scanned: **{}**".format(len(dims)))
output.print_md("- Overridden values: **{}**".format(len(flagged)))

if not flagged:
    output.print_md("\nNothing to report.")
    script.exit()

output.add_style("overridden { background-color: #ff0000; color: #fff; font-weight: bold; padding: 0 4px; }")
output.add_style("truevalue  { background-color: #1e90ff; color: #fff; font-weight: bold; padding: 0 4px; }")

for true_val, override, dim in flagged:
    output.print_html(
        "<truevalue>{}</truevalue> &nbsp; → &nbsp; <overridden>{}</overridden> &nbsp; {}"
        .format(true_val, override, output.linkify(dim.Id))
    )
