# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Apply a view filter to multiple view templates in one shot with a chosen color override.

The chosen color is applied to both cut lines and projection lines of the
filter on each target template. Templates that already carry the filter
are reported and left alone.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Apply Filters\nto Templates"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

filters = list(DB.FilteredElementCollector(doc).OfClass(DB.ParameterFilterElement))
if not filters:
    forms.alert("No view filters defined in this project.",
                title="No Filters",
                exitscript=True)
filter_by_name = {f.Name: f for f in filters}

filter_name = forms.SelectFromList.show(
    sorted(filter_by_name.keys()),
    title="Select View Filter",
    button_name="Use This Filter",
    multiselect=False,
)
if not filter_name:
    script.exit()
selected_filter = filter_by_name[filter_name]

color = forms.select_swatch(title="Select Override Color")
if color is None:
    script.exit()
revit_color = DB.Color(color.red, color.green, color.blue)

overrides = DB.OverrideGraphicSettings()
overrides.SetCutLineColor(revit_color)
overrides.SetProjectionLineColor(revit_color)

target_templates = forms.select_viewtemplates(
    title="Select View Templates",
    button_name="Apply Filter",
    multiple=True,
)
if not target_templates:
    script.exit()

applied = []
already_had = []
failed = []
with revit.Transaction("Apply View Filter To Templates"):
    for template in target_templates:
        try:
            if template.GetFilters().Contains(selected_filter.Id):
                template.SetFilterOverrides(selected_filter.Id, overrides)
                already_had.append(template.Name)
            else:
                template.AddFilter(selected_filter.Id)
                template.SetFilterOverrides(selected_filter.Id, overrides)
                applied.append(template.Name)
        except Exception as ex:
            failed.append((template.Name, str(ex)))

output = script.get_output()
output.print_md("# Apply Filter `{}`".format(filter_name))
output.print_md("**Applied to {} new template(s):**".format(len(applied)))
for name in applied:
    output.print_md("- {}".format(name))
if already_had:
    output.print_md("\n**Already carried this filter — overrides updated ({}):**".format(len(already_had)))
    for name in already_had:
        output.print_md("- {}".format(name))
if failed:
    output.print_md("\n**Failed on {}:**".format(len(failed)))
    for name, err in failed:
        output.print_md("- `{}` — {}".format(name, err))
