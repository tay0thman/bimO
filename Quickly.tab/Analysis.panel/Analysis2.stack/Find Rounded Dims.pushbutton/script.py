# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Detect dimensions whose displayed text differs from the true measurement at a chosen tolerance.

Useful for catching dims that have been visually rounded by the dim style (e.g. "10'-0\"" when the actual length is 10'-0 1/4"). User-overridden dimensions are skipped — use Find Dimension Overrides for those.
"""
from fractions import Fraction

from pyrevit import revit, DB, forms, script

__title__ = "Find Rounded\nDims"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()

TOLERANCES = {"1/16": 16, "1/32": 32, "1/64": 64, "1/128": 128, "1/256": 256}

tol_label = forms.CommandSwitchWindow.show(
    list(TOLERANCES.keys()),
    message="Tolerance — flag dims displayed less precisely than this",
)
if not tol_label:
    script.exit()
denom = TOLERANCES[tol_label]

LINEAR_SHAPES = {
    DB.DimensionShape.Linear,
    DB.DimensionShape.Radial,
    DB.DimensionShape.Diameter,
    DB.DimensionShape.ArcLength,
}


def _dec_feet_to_text(value_ft, denominator):
    """Render value (in internal feet) as feet-inches-fraction at 1/denominator-inch resolution."""
    feet = int(value_ft)
    remaining_inches = (value_ft - feet) * 12.0
    inches = int(remaining_inches)
    units = int(round((remaining_inches - inches) * denominator))
    if units == denominator:
        inches += 1
        units = 0
    if inches == 12:
        feet += 1
        inches = 0
    if units == 0:
        return '{}"'.format(inches) if feet == 0 else "{}'-{}\"".format(feet, inches)
    f = Fraction(units, denominator)  # auto-reduces 8/16 -> 1/2 etc.
    frac_text = "{}/{}".format(f.numerator, f.denominator)
    if feet == 0:
        return '{} {}"'.format(inches, frac_text)
    return "{}'-{} {}\"".format(feet, inches, frac_text)


def _normalize(s):
    """Collapse whitespace and strip a leading 0'- so the rounded text can be compared cleanly."""
    s = s.strip()
    if s.startswith("0'-"):
        s = s[3:].lstrip()
    return " ".join(s.split())


dims = list(DB.FilteredElementCollector(doc)
            .OfCategory(DB.BuiltInCategory.OST_Dimensions)
            .OfClass(DB.Dimension))

flagged = []
checked = 0
for dim in dims:
    if dim.ValueOverride:
        continue
    if dim.DimensionShape not in LINEAR_SHAPES:
        continue
    if dim.Value is None or not dim.ValueString:
        continue
    checked += 1
    rounded = _dec_feet_to_text(dim.Value, denom)
    if _normalize(dim.ValueString) != _normalize(rounded):
        flagged.append((dim.ValueString, rounded, dim))

output.print_md("# Rounded Dimensions — Tolerance {}".format(tol_label))
output.print_md("- Dimensions checked: **{}**".format(checked))
output.print_md("- Flagged: **{}**".format(len(flagged)))

if not flagged:
    script.exit()

output.add_style("dispval { background-color: #ff0000; color: #fff; font-weight: bold; padding: 0 4px; }")
output.add_style("rndval  { background-color: #1e90ff; color: #fff; font-weight: bold; padding: 0 4px; }")

for display, rounded, dim in flagged:
    output.print_html(
        "<dispval>{}</dispval> &nbsp; vs &nbsp; <rndval>{}</rndval> &nbsp; {}"
        .format(display, rounded, output.linkify(dim.Id))
    )
