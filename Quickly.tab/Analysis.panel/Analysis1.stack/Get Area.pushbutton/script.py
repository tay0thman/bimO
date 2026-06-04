# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Sum the Area parameter across the current selection and report the total in the project's area units."""
from pyrevit import revit, DB, forms, script

__title__ = "Get Area"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

elements = revit.get_selection().elements
if not elements:
    forms.alert("Select one or more area-bearing elements first (rooms, areas, floors, sheets, etc.).",
                title="No Selection",
                exitscript=True)

total_area = 0.0
counted = 0
for el in elements:
    area_param = el.LookupParameter("Area")
    if area_param and area_param.StorageType == DB.StorageType.Double:
        total_area += area_param.AsDouble()
        counted += 1

if counted == 0:
    forms.alert("None of the selected elements have an Area parameter.",
                title="No Area",
                exitscript=True)

formatted = DB.UnitFormatUtils.Format(doc.GetUnits(), DB.SpecTypeId.Area, total_area, False)
forms.alert("Total area across {} element(s):\n\n{}".format(counted, formatted),
            title="Total Area")
