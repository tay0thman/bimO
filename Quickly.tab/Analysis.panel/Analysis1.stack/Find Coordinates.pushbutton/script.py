# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Report this project's Internal Origin, Project Base Point, Survey Point, Shared Coordinates, and Angle to True North.

All distances and angles use the project's display units (set in Manage → Project Units).
"""
from pyrevit import revit, DB, script

__title__ = "Find Project\nCoordinates"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
output = script.get_output()


def _fmt_length(value_ft):
    return DB.UnitFormatUtils.Format(doc.GetUnits(), DB.SpecTypeId.Length, value_ft, False)


def _fmt_angle(value_rad):
    return DB.UnitFormatUtils.Format(doc.GetUnits(), DB.SpecTypeId.Angle, value_rad, False)


def _fmt_xyz(p):
    return "X = {}  ·  Y = {}  ·  Z = {}".format(
        _fmt_length(p.X), _fmt_length(p.Y), _fmt_length(p.Z))


base_pt = DB.BasePoint.GetProjectBasePoint(doc).Position
survey_pt = DB.BasePoint.GetSurveyPoint(doc).Position
base_shared = DB.BasePoint.GetProjectBasePoint(doc).SharedPosition
active_location = doc.ActiveProjectLocation
project_position = active_location.GetProjectPosition(DB.XYZ.Zero)
shared_origin = active_location.GetTransform().Origin

output.print_md("# Project Coordinates")

output.print_md("## Base Points")
output.print_md("- **Internal Origin:** X = 0, Y = 0, Z = 0")
output.print_md("- **Project Base Point:** {}".format(_fmt_xyz(base_pt)))
output.print_md("- **Survey Point:** {}".format(_fmt_xyz(survey_pt)))

output.print_md("## Base → Survey Deltas")
output.print_md("- **ΔX:** {}".format(_fmt_length(survey_pt.X - base_pt.X)))
output.print_md("- **ΔY:** {}".format(_fmt_length(survey_pt.Y - base_pt.Y)))
output.print_md("- **ΔZ (project elevation):** {}".format(_fmt_length(survey_pt.Z - base_pt.Z)))

output.print_md("## Shared Coordinates")
output.print_md("- **Transform origin:** {}".format(_fmt_xyz(shared_origin)))
output.print_md("- **Base Point shared position:** {}".format(_fmt_xyz(base_shared)))

output.print_md("## Orientation")
output.print_md("- **Angle to True North:** {}".format(_fmt_angle(project_position.Angle)))
