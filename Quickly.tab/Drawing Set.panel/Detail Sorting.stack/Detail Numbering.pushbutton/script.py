# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Auto-number every viewport on the active sheet based on its position.

The active view must be a sheet. Viewports are mapped to a 5-column × 4-row
grid tuned to a 30"×42" landscape titleblock; cells are numbered 1..20
left-to-right within each row, top-to-bottom.

Two passes:
1. Stamp every viewport with a unique "Xx<n>" placeholder so subsequent
   real numbers don't collide with currently-assigned ones.
2. Assign the position-based number to each viewport.
"""
import random

from pyrevit import revit, DB, forms, script

__title__ = "Detail\nNumbering"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

# 5 columns × 4 rows, tuned for a 30"x42" landscape sheet.
X_DOMAINS = [(2.5, 3.1), (1.91, 2.5), (1.32, 1.91), (0.731, 1.32), (0, 0.731)]
Y_DOMAINS = [(1.85, 2.5), (1.25, 1.85), (0.656, 1.25), (0, 0.731)]

doc = revit.doc
active_view = revit.active_view

if not isinstance(active_view, DB.ViewSheet):
    forms.alert("Activate a sheet view first — this tool numbers viewports placed on the active sheet.",
                title="Not a Sheet",
                exitscript=True)

viewports = list(DB.FilteredElementCollector(doc, active_view.Id).OfClass(DB.Viewport))
if not viewports:
    forms.alert("The active sheet has no viewports.",
                title="No Viewports",
                exitscript=True)

cells = []  # ordered (left-to-right within each row, top-to-bottom)
for x_lo, x_hi in X_DOMAINS:
    for y_lo, y_hi in Y_DOMAINS:
        cells.append(((x_lo, x_hi), (y_lo, y_hi)))


def _cell_index_for(viewport):
    center = viewport.GetBoxCenter()
    lower_left = viewport.GetBoxOutline().MinimumPoint
    mid = DB.XYZ((lower_left.X + center.X) / 2.0, (lower_left.Y + center.Y) / 2.0, 0)
    quarter = DB.XYZ((lower_left.X + mid.X) / 2.0, (lower_left.Y + mid.Y) / 2.0, 0)
    for k, ((x_lo, x_hi), (y_lo, y_hi)) in enumerate(cells):
        if x_lo <= quarter.X <= x_hi and y_lo <= quarter.Y <= y_hi:
            return k + 1
    return None


# Pass 1 — stamp every viewport with a unique placeholder to break duplicate-number conflicts.
with revit.Transaction("Detail Numbering — placeholder pass"):
    for viewport in viewports:
        view = doc.GetElement(viewport.ViewId)
        placeholder = "Xx{}".format(random.randint(1, 99999))
        param = view.get_Parameter(DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
        if param and not param.IsReadOnly:
            param.Set(placeholder)

# Pass 2 — assign the final position-based number.
numbered = 0
unplaced = []
with revit.Transaction("Detail Numbering"):
    for viewport in viewports:
        view = doc.GetElement(viewport.ViewId)
        index = _cell_index_for(viewport)
        if index is None:
            unplaced.append(view.Name)
            continue
        param = view.get_Parameter(DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
        if param and not param.IsReadOnly:
            param.Set(str(index))
            numbered += 1
        print("{:>3} — {}".format(index, view.Name))

forms.toast("Numbered {} viewport(s)".format(numbered), title="Detail Numbering")
if unplaced:
    print("\nViewports that fell outside the 5×4 grid (left as placeholder):")
    for name in unplaced:
        print("  - {}".format(name))
