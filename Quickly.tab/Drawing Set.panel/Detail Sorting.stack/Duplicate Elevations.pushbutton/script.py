# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Duplicate selected elevation views with a user-supplied prefix and apply a chosen elevation view template to the copies."""
from pyrevit import revit, DB, forms, script

__title__ = "Duplicate\nElevations"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

all_views = (DB.FilteredElementCollector(doc)
             .OfCategory(DB.BuiltInCategory.OST_Views)
             .WhereElementIsNotElementType()
             .ToElements())

elevations = [v for v in all_views
              if v.ViewType == DB.ViewType.Elevation and not v.IsTemplate]
if not elevations:
    forms.alert("No elevation views found in this project.",
                title="No Elevations",
                exitscript=True)

elevation_by_name = {v.Name: v for v in elevations}
selected_names = forms.SelectFromList.show(
    sorted(elevation_by_name.keys()),
    title="Select Elevations to Duplicate",
    button_name="Duplicate",
    multiselect=True,
)
if not selected_names:
    script.exit()
selected_elevations = [elevation_by_name[n] for n in selected_names]

prefix = forms.ask_for_string(default="UG - ",
                              prompt="Prefix for the new view names:",
                              title="Duplicate Elevations")
if prefix is None:
    script.exit()

elevation_templates = [v for v in all_views
                       if v.IsTemplate and v.ViewType == DB.ViewType.Elevation]
if not elevation_templates:
    forms.alert("No elevation view templates found in this project. Create one first.",
                title="No Elevation Templates",
                exitscript=True)
template_by_name = {t.Name: t for t in elevation_templates}
selected_template_name = forms.SelectFromList.show(
    sorted(template_by_name.keys()),
    title="Select Elevation View Template",
    button_name="Apply Template",
    multiselect=False,
)
if not selected_template_name:
    script.exit()
selected_template = template_by_name[selected_template_name]

created = []
with revit.Transaction("Duplicate Elevations"):
    for original in selected_elevations:
        new_view_id = original.Duplicate(DB.ViewDuplicateOption.WithDetailing)
        new_view = doc.GetElement(new_view_id)
        new_view.Name = prefix + original.Name
        new_view.ViewTemplateId = selected_template.Id
        created.append(new_view)

output = script.get_output()
output.print_md("# Duplicate Elevations")
output.print_md("**Created {} new elevation(s):**".format(len(created)))
for v in created:
    output.print_md("- {} — {}".format(output.linkify(v.Id), v.Name))
