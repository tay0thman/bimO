# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Translate the crop boxes of selected views on a sheet by an X / Y / Z offset (in feet).

Workflow:
1. Pick a sheet.
2. Pick the views on that sheet whose crop boxes you want to nudge.
3. Enter X, Y, Z translation values in feet.

Note: filled-region and some detail elements may not move with the view —
they're tied to the view rather than the crop box.
"""
from pyrevit import revit, DB, forms, script

__title__ = "View Pan"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

sheet = forms.select_sheets(title="Select Sheet",
                            button_name="Use This Sheet",
                            multiple=False)
if not sheet:
    script.exit()

view_ids = list(sheet.GetAllPlacedViews())
if not view_ids:
    forms.alert("The selected sheet has no views placed on it.",
                title="No Views",
                exitscript=True)
views_by_name = {doc.GetElement(vid).Name: doc.GetElement(vid) for vid in view_ids}

selected_view_names = forms.SelectFromList.show(
    sorted(views_by_name.keys()),
    button_name="Pan These Views",
    multiselect=True,
)
if not selected_view_names:
    script.exit()
selected_views = [views_by_name[n] for n in selected_view_names]


def _ask_translation(axis):
    return forms.ask_for_number_slider(
        default=0, interval=1, min=-100, max=100,
        prompt="Translation in feet ({})".format(axis),
        title="{} Translation".format(axis),
    )


x = _ask_translation("X")
y = _ask_translation("Y")
z = _ask_translation("Z")
if x is None or y is None or z is None:
    script.exit()
translate = DB.XYZ(x, y, z)

non_type_filter = DB.ElementIsElementTypeFilter(True)
moved = 0
failed = []
with revit.Transaction("Pan Views"):
    for view in selected_views:
        view.CropBoxVisible = True
        dependent_ids = view.GetDependentElements(non_type_filter)
        if not dependent_ids:
            failed.append((view.Name, "view has no dependent crop element"))
            continue
        dependent = doc.GetElement(dependent_ids[0])
        try:
            dependent.Location.Move(translate)
            moved += 1
        except Exception as ex:
            failed.append((view.Name, str(ex)))
        view.CropBoxVisible = False
        view.CropBoxActive = True

output = script.get_output()
output.print_md("# View Pan")
output.print_md("**Panned {} view(s) by ΔX={} ΔY={} ΔZ={} ft.**".format(moved, x, y, z))
if failed:
    output.print_md("\n**Skipped:**")
    for name, reason in failed:
        output.print_md("- `{}` — {}".format(name, reason))
