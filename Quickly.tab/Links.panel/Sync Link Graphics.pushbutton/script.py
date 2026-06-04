# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Copy a Revit link's graphic overrides from a source view template to multiple target view templates.

Workflow:
1. Pick the Revit link whose overrides you want to propagate.
2. Pick the source view template that already has the desired overrides for that link.
3. Pick one or more target view templates to push those overrides to.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Sync Link\nGraphics"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

link_types = list(DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType))
if not link_types:
    forms.alert("No Revit links found in this project.",
                title="No Links",
                exitscript=True)

link_by_name = {lt.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): lt
                for lt in link_types}

selected_link_name = forms.SelectFromList.show(
    sorted(link_by_name.keys()),
    title="Select Revit Link",
    button_name="Use This Link",
    multiselect=False,
)
if not selected_link_name:
    script.exit()
selected_link = link_by_name[selected_link_name]
link_id = selected_link.Id

source_template = forms.select_viewtemplates(
    title="Select SOURCE View Template (the one with the overrides you want to copy)",
    button_name="Use As Source",
    multiple=False,
)
if not source_template:
    script.exit()

target_templates = forms.select_viewtemplates(
    title="Select TARGET View Templates (overrides will be pushed to these)",
    button_name="Apply Overrides",
)
if not target_templates:
    script.exit()

source_overrides = source_template.GetLinkOverrides(link_id)

succeeded = []
failed = []
with revit.Transaction("Sync Link Graphic Overrides"):
    for vt in target_templates:
        try:
            vt.SetLinkOverrides(link_id, source_overrides)
            succeeded.append(vt.Name)
        except Exception as ex:
            failed.append((vt.Name, str(ex)))

output = script.get_output()
output.print_md("# Sync Link Graphics — {}".format(selected_link_name))
output.print_md("**Source template:** {}".format(source_template.Name))
output.print_md("\n**Applied to {} template(s):**".format(len(succeeded)))
for name in succeeded:
    output.print_md("- {}".format(name))
if failed:
    output.print_md("\n**Failed on {} template(s):**".format(len(failed)))
    for name, err in failed:
        output.print_md("- `{}` — {}".format(name, err))
