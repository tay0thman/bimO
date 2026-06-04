# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Select all walls of the chosen types whose top is currently attached, scoped to picked levels or the active view.

Workflow:
1. Pick one or more levels (or cancel the level picker to scope to the active view instead).
2. Pick one or more wall types from the project.
3. The script selects every wall whose type matches one of those picked
   AND whose `Top is Attached` flag is on.
"""
from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List

__title__ = "Select Attached\nWalls by Type"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
uidoc = revit.uidoc

levels = forms.select_levels(
    title="Select Levels  (Cancel to use the Active View)",
    button_name="Use These Levels",
    multiple=True,
)
use_active_view = not levels
level_ids = {lvl.Id for lvl in levels} if levels else set()

wall_types = (DB.FilteredElementCollector(doc)
              .OfCategory(DB.BuiltInCategory.OST_Walls)
              .WhereElementIsElementType()
              .ToElements())
wall_type_by_name = {wt.Name: wt for wt in wall_types}
selected_type_names = forms.SelectFromList.show(
    sorted(wall_type_by_name.keys()),
    title="Select Wall Types",
    button_name="Select",
    multiselect=True,
)
if not selected_type_names:
    script.exit()
selected_type_ids = {wall_type_by_name[n].Id for n in selected_type_names}

if use_active_view:
    candidate_walls = (DB.FilteredElementCollector(doc, uidoc.ActiveView.Id)
                       .OfCategory(DB.BuiltInCategory.OST_Walls)
                       .WhereElementIsNotElementType()
                       .ToElements())
else:
    all_walls = (DB.FilteredElementCollector(doc)
                 .OfCategory(DB.BuiltInCategory.OST_Walls)
                 .WhereElementIsNotElementType()
                 .ToElements())
    candidate_walls = [w for w in all_walls
                       if w.LevelId in level_ids and w.CanHaveProfileSketch()]

matched_walls = []
for wall in candidate_walls:
    if wall.GetTypeId() not in selected_type_ids:
        continue
    top_attached = wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_IS_ATTACHED)
    if top_attached and top_attached.AsInteger() == 1:
        matched_walls.append(wall)

if not matched_walls:
    forms.alert("No walls match the selected types with `Top is Attached` enabled.",
                title="No Matches",
                exitscript=True)

uidoc.Selection.SetElementIds(List[DB.ElementId]([w.Id for w in matched_walls]))
