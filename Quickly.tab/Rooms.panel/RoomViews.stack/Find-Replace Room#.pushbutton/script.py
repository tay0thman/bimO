# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Renumber view names and view titles to track renumbered rooms.

Workflow when a project's room numbers change:
1. Before renumbering, store each room's existing number in a project-wide
   shared parameter named `Room Numbers - Old` on the room.
2. Renumber the rooms in Revit as normal (changing each room's `Number`).
3. Run this tool — every view whose name or title contains an old number
   gets that number replaced with the room's current `Number`.

A "number" here is any 3-digit token in the view name or view title.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Find/Replace\nRoom #"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

OLD_ROOM_PARAM = "Room Numbers - Old"

doc = revit.doc


def _find_three_digit_token(text):
    """Return the first 3-digit whitespace-separated token in text, or None."""
    if not text:
        return None
    for word in text.split():
        if word.isdigit() and len(word) == 3:
            return word
    return None


def _collect_views(active_doc):
    return (DB.FilteredElementCollector(active_doc)
            .OfCategory(DB.BuiltInCategory.OST_Views)
            .WhereElementIsNotElementType()
            .ToElements())


rooms = (DB.FilteredElementCollector(doc)
         .OfClass(DB.SpatialElement)
         .ToElements())
rooms = [r for r in rooms if isinstance(r, DB.Architecture.Room) and r.Number]

if not rooms:
    forms.alert("No rooms found in the project.", title="No Rooms", exitscript=True)

# Build old-number → new-number map from the shared parameter on each room.
renumbers = {}
for room in rooms:
    old_param = room.LookupParameter(OLD_ROOM_PARAM)
    if not old_param:
        continue
    old_number = old_param.AsString()
    if old_number and old_number != room.Number:
        renumbers[old_number] = room.Number

if not renumbers:
    forms.alert("No `{}` values found on any room, or no rooms were renumbered.\n\n"
                "Add a project shared parameter named `{}` to rooms and populate it "
                "with each room's previous number before running this tool."
                .format(OLD_ROOM_PARAM, OLD_ROOM_PARAM),
                title="Nothing To Do",
                exitscript=True)

views = _collect_views(doc)
renamed_count = 0

with revit.Transaction("Find / Replace Room # in View Names"):
    for view in views:
        title_param = view.get_Parameter(DB.BuiltInParameter.VIEW_DESCRIPTION)
        view_title = title_param.AsString() if title_param else None

        if view_title:
            token = _find_three_digit_token(view_title)
            if token and token in renumbers:
                new_title = view_title.replace(token, renumbers[token])
                title_param.Set(new_title)
                print("Title: '{}' → '{}'".format(view_title, new_title))
                renamed_count += 1
                continue

        view_name = revit.query.get_name(view)
        token = _find_three_digit_token(view_name)
        if token and token in renumbers:
            name_param = view.get_Parameter(DB.BuiltInParameter.VIEW_NAME)
            if name_param and not name_param.IsReadOnly:
                new_name = view_name.replace(token, renumbers[token])
                name_param.Set(new_name)
                print("Name:  '{}' → '{}'".format(view_name, new_name))
                renamed_count += 1

print("\nDone. Renamed {} view(s).".format(renamed_count))
