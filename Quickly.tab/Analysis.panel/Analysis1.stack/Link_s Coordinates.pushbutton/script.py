# -*- coding: utf-8 -*-
# Author: Tay Othman
"""For each selected Revit link, report its Internal Origin, Base Point, Survey Point, Shared Coordinates, and Angle to True North.

Each report uses the link document's own display units. Unloaded links are reported with a notice and skipped.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Find Link's\nCoordinates"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

main_doc = revit.doc
output = script.get_output()


def _fmt_length(d, value_ft):
    return DB.UnitFormatUtils.Format(d.GetUnits(), DB.SpecTypeId.Length, value_ft, False)


def _fmt_angle(d, value_rad):
    return DB.UnitFormatUtils.Format(d.GetUnits(), DB.SpecTypeId.Angle, value_rad, False)


def _fmt_xyz(d, p):
    return "X = {}  ·  Y = {}  ·  Z = {}".format(
        _fmt_length(d, p.X), _fmt_length(d, p.Y), _fmt_length(d, p.Z))


class _LinkItem(forms.TemplateListItem):
    @property
    def name(self):
        return self.unwrap().Name.replace("<", "").replace(">", "")


link_instances = [li for li in DB.FilteredElementCollector(main_doc)
                  .OfClass(DB.RevitLinkInstance)
                  if li.IsValidObject]
if not link_instances:
    forms.alert("No Revit links found in the project.",
                title="No Links",
                exitscript=True)

selected = forms.SelectFromList.show(
    [_LinkItem(li) for li in link_instances],
    title="Select Revit Links",
    button_name="Report Coordinates",
    multiselect=True,
)
if not selected:
    script.exit()

output.print_md("# Link Coordinates Report")

for link in selected:
    link_doc = link.GetLinkDocument()
    link_name = link.Name.replace("<", "").replace(">", "")

    output.print_md("## {}".format(link_name))

    if not link_doc:
        output.print_md("> _Link is not loaded — cannot analyze._")
        continue

    base_pt = DB.BasePoint.GetProjectBasePoint(link_doc).Position
    survey_pt = DB.BasePoint.GetSurveyPoint(link_doc).Position
    base_shared = DB.BasePoint.GetProjectBasePoint(link_doc).SharedPosition
    active_location = link_doc.ActiveProjectLocation
    project_position = active_location.GetProjectPosition(DB.XYZ.Zero)
    shared_origin = active_location.GetTransform().Origin

    output.print_md("**Base Points**")
    output.print_md("- Internal Origin: X = 0, Y = 0, Z = 0")
    output.print_md("- Project Base Point: {}".format(_fmt_xyz(link_doc, base_pt)))
    output.print_md("- Survey Point: {}".format(_fmt_xyz(link_doc, survey_pt)))

    output.print_md("**Base → Survey Deltas**")
    output.print_md("- ΔX: {}".format(_fmt_length(link_doc, survey_pt.X - base_pt.X)))
    output.print_md("- ΔY: {}".format(_fmt_length(link_doc, survey_pt.Y - base_pt.Y)))
    output.print_md("- ΔZ: {}".format(_fmt_length(link_doc, survey_pt.Z - base_pt.Z)))

    output.print_md("**Shared Coordinates**")
    output.print_md("- Transform origin: {}".format(_fmt_xyz(link_doc, shared_origin)))
    output.print_md("- Base Point shared position: {}".format(_fmt_xyz(link_doc, base_shared)))

    output.print_md("**Orientation**")
    output.print_md("- Angle to True North: {}".format(_fmt_angle(link_doc, project_position.Angle)))
