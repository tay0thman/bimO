# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Auto-number every viewport on the active sheet based on its position.

The active view must be a sheet. Viewports are grouped into rows (top-to-bottom)
and numbered left-to-right within each row, derived from the viewports' actual
positions on the sheet — so it works on any titleblock size, not just 30"x42".

Two passes:
1. Stamp every viewport with a unique "Xx<n>" placeholder so the final numbers
   can never collide with a number currently in use on the sheet.
2. Assign the position-based number to each viewport.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Detail\nNumbering"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
active_view = revit.active_view
output = script.get_output()

if not isinstance(active_view, DB.ViewSheet):
    forms.alert("Activate a sheet view first — this tool numbers the viewports "
                "placed on the active sheet.",
                title="Not a Sheet", exitscript=True)

viewports = list(DB.FilteredElementCollector(doc, active_view.Id)
                 .OfClass(DB.Viewport))
if not viewports:
    forms.alert("The active sheet has no viewports.",
                title="No Viewports", exitscript=True)


def detail_number_param(viewport):
    """The settable 'Detail Number' lives on the Viewport, not the View it shows."""
    return viewport.get_Parameter(DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER)


def view_name(viewport):
    view = doc.GetElement(viewport.ViewId)
    return view.Name if view else "<{}>".format(viewport.Id)


# Build (viewport, center_x, center_y, height) for each viewport, in sheet feet.
entries = []
for vp in viewports:
    outline = vp.GetBoxOutline()
    lo, hi = outline.MinimumPoint, outline.MaximumPoint
    entries.append((vp,
                    (lo.X + hi.X) / 2.0,
                    (lo.Y + hi.Y) / 2.0,
                    abs(hi.Y - lo.Y)))

# Row tolerance: half the typical viewport height (min 1"). Viewports whose
# centers are vertically closer than this count as the same row.
heights = sorted(e[3] for e in entries)
median_h = heights[len(heights) // 2]
row_tol = max(median_h * 0.5, 1.0 / 12.0)

# Group into rows top-to-bottom; a vertical gap larger than row_tol starts a row.
entries.sort(key=lambda e: -e[2])
rows = []
current = []
prev_y = None
for entry in entries:
    if prev_y is not None and (prev_y - entry[2]) > row_tol:
        rows.append(current)
        current = []
    current.append(entry)
    prev_y = entry[2]
if current:
    rows.append(current)

# Within each row, order left-to-right by center X.
ordered = []
for row in rows:
    row.sort(key=lambda e: e[1])
    ordered.extend(row)

output.print_md("## Detail Numbering")
output.print_md("Sheet **{}** — {}".format(active_view.SheetNumber, active_view.Name))

# Pass 1 — unique placeholders so the final numbers can't collide with current ones.
with revit.Transaction("Detail Numbering — placeholder pass"):
    for i, entry in enumerate(ordered, start=1):
        param = detail_number_param(entry[0])
        if param and not param.IsReadOnly:
            param.Set("Xx{}".format(i))

# Pass 2 — assign the position-based number, per-item so one failure can't roll
# back the whole batch (e.g. a read-only viewport that still holds a clashing number).
numbered = 0
skipped = []
with revit.Transaction("Detail Numbering"):
    for i, entry in enumerate(ordered, start=1):
        vp = entry[0]
        name = view_name(vp)
        param = detail_number_param(vp)
        if not param or param.IsReadOnly:
            skipped.append("{} — Detail Number is read-only".format(name))
            continue
        try:
            param.Set(str(i))
            numbered += 1
            output.print_md("**{}** — {}".format(i, name))
        except Exception as err:
            skipped.append("{} — {}".format(name, err))

output.print_md("---")
output.print_md("Numbered **{}** of {} viewport(s) across {} row(s)."
                .format(numbered, len(ordered), len(rows)))
if skipped:
    output.print_md("**Skipped {}:**".format(len(skipped)))
    for line in skipped:
        output.print_md("- {}".format(line))
