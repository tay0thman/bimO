# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Create an isometric 3D view for each selected room.

For every room you pick, this tool creates a new isometric View3D whose section
box is sized to that room's 3D bounding box. Each view is set to 1/4"=1'-0",
Architectural discipline, and gets the chosen 3D view template applied.

Views named `ROOM AXON _ <Number> - <Name>` that already exist are replaced.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Room Axon"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

VIEW_NAME_PREFIX = "ROOM AXON _ "
VIEW_SCALE = 48  # 1/4" = 1'-0"

doc = revit.doc
uidoc = revit.uidoc


def _room_label(room):
    number = room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() or ""
    name = room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString() or ""
    return "{} - {}".format(number, name)


def _view_name_for(room):
    return VIEW_NAME_PREFIX + _room_label(room)


levels = (DB.FilteredElementCollector(doc)
          .OfCategory(DB.BuiltInCategory.OST_Levels)
          .WhereElementIsNotElementType()
          .ToElements())
level_by_name = {lvl.Name: lvl for lvl in levels}
level_name = forms.SelectFromList.show(
    sorted(level_by_name.keys()),
    title="Select Level",
    button_name="Pick Level",
)
if not level_name:
    script.exit()
selected_level = level_by_name[level_name]

all_rooms = (DB.FilteredElementCollector(doc)
             .OfCategory(DB.BuiltInCategory.OST_Rooms)
             .WhereElementIsNotElementType()
             .ToElements())
rooms_on_level = [r for r in all_rooms
                  if r.LevelId == selected_level.Id and r.Area > 0]
if not rooms_on_level:
    forms.alert("No placed rooms found on level '{}'.".format(level_name),
                title="No Rooms",
                exitscript=True)
rooms_on_level.sort(key=lambda r: r.Number or "")

room_by_label = {_room_label(r): r for r in rooms_on_level}
ordered_labels = [_room_label(r) for r in rooms_on_level]
selected_labels = forms.SelectFromList.show(
    ordered_labels,
    title="Select Rooms",
    button_name="Create Axon Views",
    multiselect=True,
)
if not selected_labels:
    script.exit()
selected_rooms = [room_by_label[label] for label in selected_labels]

templates = [v for v in DB.FilteredElementCollector(doc).OfClass(DB.View)
             if v.IsTemplate and v.ViewType == DB.ViewType.ThreeD]
if not templates:
    forms.alert("No 3D view templates found in the project. Create one first.",
                title="No 3D Templates",
                exitscript=True)
template_by_name = {t.Name: t for t in templates}
template_name = forms.SelectFromList.show(
    sorted(template_by_name.keys()),
    title="Select 3D View Template",
    button_name="Apply Template",
)
if not template_name:
    script.exit()
template = template_by_name[template_name]

view3d_type = next((t for t in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
                    if t.ViewFamily == DB.ViewFamily.ThreeDimensional), None)
if not view3d_type:
    forms.alert("Could not find a 3D view family type in the project.",
                title="No 3D View Type",
                exitscript=True)

# If the active view is one of the views we're about to delete-and-recreate,
# navigate away first so Revit doesn't choke on an active-view delete.
existing_views_3d = list(DB.FilteredElementCollector(doc)
                         .OfClass(DB.View3D)
                         .WhereElementIsNotElementType()
                         .ToElements())
existing_by_name = {v.Name: v for v in existing_views_3d}
target_names = {_view_name_for(r) for r in selected_rooms}
active_view = doc.ActiveView
if active_view and active_view.Name in target_names:
    starting_view_id = DB.StartingViewSettings.GetStartingViewSettings(doc).ViewId
    starting_view = doc.GetElement(starting_view_id)
    if starting_view:
        uidoc.ActiveView = starting_view

created_views = []
skipped_rooms = []
with revit.Transaction("Create Room Axon Views"):
    for room in selected_rooms:
        bbox = room.get_BoundingBox(None)
        if not bbox:
            skipped_rooms.append(_room_label(room))
            continue
        existing = existing_by_name.get(_view_name_for(room))
        if existing:
            doc.Delete(existing.Id)
        view3d = DB.View3D.CreateIsometric(doc, view3d_type.Id)
        view3d.SetSectionBox(bbox)
        view3d.Name = _view_name_for(room)
        view3d.Scale = VIEW_SCALE
        view3d.Discipline = DB.ViewDiscipline.Architectural
        view3d.ViewTemplateId = template.Id
        created_views.append(view3d)

output = script.get_output()
output.print_md("### Room Axon Views")
output.print_md("**Created: {}**".format(len(created_views)))
for v in created_views:
    output.print_md("- {} — {}".format(output.linkify(v.Id), v.Name))
if skipped_rooms:
    output.print_md("\n**Skipped (no 3D bounding box): {}**".format(len(skipped_rooms)))
    for label in skipped_rooms:
        output.print_md("- {}".format(label))

if created_views:
    uidoc.ActiveView = created_views[-1]
