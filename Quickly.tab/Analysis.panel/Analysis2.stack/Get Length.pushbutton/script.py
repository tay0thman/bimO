# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Sum lengths of selected walls (location curve) and curve-element lines/arcs."""
from pyrevit import revit, DB, forms, script

__title__ = "Get Length"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

elements = revit.get_selection().elements
if not elements:
    forms.alert("Select walls or line / curve elements first.",
                title="No Selection",
                exitscript=True)

total_length = 0.0
counted = 0
for el in elements:
    if isinstance(el, DB.Wall) and isinstance(el.Location, DB.LocationCurve):
        total_length += el.Location.Curve.Length
        counted += 1
    elif isinstance(el, DB.CurveElement) and el.GeometryCurve:
        total_length += el.GeometryCurve.Length
        counted += 1

if counted == 0:
    forms.alert("None of the selected elements have a length (walls or curve-based annotations).",
                title="No Length",
                exitscript=True)

formatted = DB.UnitFormatUtils.Format(doc.GetUnits(), DB.SpecTypeId.Length, total_length, False)
forms.alert("Total length across {} element(s):\n\n{}".format(counted, formatted),
            title="Total Length")
