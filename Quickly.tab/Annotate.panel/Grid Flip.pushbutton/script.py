# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Toggle grid-bubble visibility at each end of every selected grid in the active view.

For each selected grid, bubbles that are currently visible at an end are hidden,
and bubbles that are currently hidden are shown — independently per end. Combined
with selecting a row of grids, this is the fastest way to "flip" bubbles from one
side of a plan to the other.
"""
from pyrevit import revit, DB, forms

__title__ = "Flip Grids"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
active_view = doc.ActiveView

grids = [obj for obj in revit.get_selection() if isinstance(obj, DB.Grid)]
if not grids:
    forms.alert("Select one or more grids first, then run this tool.",
                title="No Grids Selected",
                warn_icon=True,
                exitscript=True)

with revit.Transaction("Flip Grids"):
    for grid in grids:
        for end in (DB.DatumEnds.End0, DB.DatumEnds.End1):
            if grid.IsBubbleVisibleInView(end, active_view):
                grid.HideBubbleInView(end, active_view)
            else:
                grid.ShowBubbleInView(end, active_view)
