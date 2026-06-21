# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Detect dimensions whose displayed text is off from the true measurement by at least a chosen tolerance.

Catches dims visually rounded by their dimension style (e.g. "10'-0\"" shown for
an actual 10'-0 1/4"). Works in any project units: the displayed text is parsed
back to a length with Revit's own unit parser and compared numerically to the
true value, so metric projects no longer false-positive. Both single- and
multi-segment dimensions are checked. User-overridden values are skipped (use
Find Dimension Overrides for those).
"""
from pyrevit import revit, DB, forms, script

__title__ = "Find Rounded\nDims"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()
units = doc.GetUnits()

# Tolerances given as inch fractions but applied as absolute lengths, so they
# remain meaningful in metric projects too.
TOLERANCES = {"1/16\"": 16.0, "1/32\"": 32.0, "1/64\"": 64.0, "1/128\"": 128.0, "1/256\"": 256.0}

LINEAR_SHAPES = {
    DB.DimensionShape.Linear,
    DB.DimensionShape.Radial,
    DB.DimensionShape.Diameter,
    DB.DimensionShape.ArcLength,
}

tol_label = forms.CommandSwitchWindow.show(
    list(TOLERANCES.keys()),
    message="Tolerance — flag dims whose display is off by at least this",
)
if not tol_label:
    script.exit()
tol_ft = (1.0 / TOLERANCES[tol_label]) / 12.0   # tolerance in internal feet


def has_override(value_override):
    return bool(value_override) and value_override.strip() != ""


def parse_length(text):
    """Parse a displayed length string back to internal feet, or None if unparseable."""
    try:
        ok, value = DB.UnitFormatUtils.TryParse(units, DB.SpecTypeId.Length, text)
        return value if ok else None
    except Exception:
        return None


def iter_segments(dim):
    """Yield (true_value, display_text, override_text) for each measured value."""
    if dim.NumberOfSegments > 0:
        for seg in dim.Segments:
            yield seg.Value, seg.ValueString, seg.ValueOverride
    else:
        yield dim.Value, dim.ValueString, dim.ValueOverride


dims = list(DB.FilteredElementCollector(doc)
            .OfCategory(DB.BuiltInCategory.OST_Dimensions)
            .OfClass(DB.Dimension))

flagged = []
checked = 0
for dim in dims:
    if dim.DimensionShape not in LINEAR_SHAPES:
        continue
    for true_val, display, override in iter_segments(dim):
        if has_override(override):
            continue
        if true_val is None or not display:
            continue
        parsed = parse_length(display)
        if parsed is None:
            continue
        checked += 1
        if abs(true_val - parsed) >= tol_ft - 1e-9:
            flagged.append((display, true_val, dim))

output.print_md("# Rounded Dimensions — Tolerance {}".format(tol_label))
output.print_md("- Dimension values checked: **{}**".format(checked))
output.print_md("- Flagged: **{}**".format(len(flagged)))

if not flagged:
    script.exit()

output.add_style("dispval { background-color: #ff0000; color: #fff; font-weight: bold; padding: 0 4px; }")
output.add_style("rndval  { background-color: #1e90ff; color: #fff; font-weight: bold; padding: 0 4px; }")

for display, true_val, dim in flagged:
    try:
        true_text = DB.UnitFormatUtils.Format(units, DB.SpecTypeId.Length, true_val, True)
    except Exception:
        true_text = "{:.4f} ft".format(true_val)
    output.print_html(
        "<dispval>{}</dispval> &nbsp; displayed vs actual &nbsp; <rndval>{}</rndval> &nbsp; {}"
        .format(display, true_text, output.linkify(dim.Id))
    )
