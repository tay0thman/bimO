# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Find every view placed on a sheet whose name contains lowercase letters and uppercase the picked ones in one transaction."""
from pyrevit import revit, DB, forms, script

__title__ = "Capitalize\nView Names"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

viewports = list(DB.FilteredElementCollector(doc).OfClass(DB.Viewport))
candidates = []  # list of (view_element, current_name)
for vp in viewports:
    view = doc.GetElement(vp.ViewId)
    name = view.Name
    if any(c.islower() for c in name):
        candidates.append((view, name))

if not candidates:
    forms.alert("All views on sheets are already fully uppercase.",
                title="Nothing To Do",
                exitscript=True)

selected_names = forms.SelectFromList.show(
    sorted({name for _, name in candidates}),
    title="Pick views to uppercase",
    button_name="Capitalize",
    multiselect=True,
)
if not selected_names:
    script.exit()

selected_set = set(selected_names)
to_update = [(v, n) for v, n in candidates if n in selected_set]

with revit.Transaction("Capitalize View Names"):
    for view, old_name in to_update:
        param = view.get_Parameter(DB.BuiltInParameter.VIEW_NAME)
        if param and not param.IsReadOnly:
            param.Set(old_name.upper())
            print("{} >>>>>> {}".format(old_name, old_name.upper()))

forms.toast("Capitalized {} view(s)".format(len(to_update)), title="Capitalize View Names")
