# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Renumber view names and titles to track renumbered rooms.

Workflow when a project's room numbers change:
1. Before renumbering, store each room's existing number in a project-wide
   shared parameter named `Room Numbers - Old` on the room.
2. Renumber the rooms in Revit as normal (changing each room's `Number`).
3. Run this tool — every view whose name or title contains an old number gets
   that number replaced with the room's current `Number`.

Old numbers may be any format (not just 3 digits) and are matched on token
boundaries in a single pass, so "101" is never replaced inside "1010" or "A101",
and a replaced value can't be re-matched by another rule.
"""
import re

from pyrevit import revit, DB, forms, script

__title__ = "Find/Replace\nRoom #"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

OLD_ROOM_PARAM = "Room Numbers - Old"

doc = revit.doc
output = script.get_output()

rooms = (DB.FilteredElementCollector(doc)
         .OfClass(DB.SpatialElement)
         .ToElements())
rooms = [r for r in rooms if isinstance(r, DB.Architecture.Room) and r.Number]
if not rooms:
    forms.alert("No rooms found in the project.", title="No Rooms", exitscript=True)

# old number -> new number, from the shared parameter on each room.
renumbers = {}
for room in rooms:
    old_param = room.LookupParameter(OLD_ROOM_PARAM)
    if not old_param:
        continue
    old_number = old_param.AsString()
    if old_number and old_number != room.Number:
        renumbers[old_number] = room.Number

if not renumbers:
    forms.alert("No `{0}` values found on any room, or no rooms were renumbered.\n\n"
                "Add a project shared parameter named `{0}` to rooms and populate it "
                "with each room's previous number before running this tool."
                .format(OLD_ROOM_PARAM),
                title="Nothing To Do", exitscript=True)

# Single-pass, boundary-aware replacement of every old number. Longest keys
# first so e.g. "1012" wins over "101"; lookarounds keep matches whole-token.
_keys = sorted(renumbers.keys(), key=len, reverse=True)
_pattern = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(k) for k in _keys) + r")(?![A-Za-z0-9])")


def _renumber(text):
    if not text:
        return text
    return _pattern.sub(lambda m: renumbers[m.group(1)], text)


views = (DB.FilteredElementCollector(doc)
         .OfCategory(DB.BuiltInCategory.OST_Views)
         .WhereElementIsNotElementType()
         .ToElements())

renamed_count = 0
errors = []
output.print_md("## Find / Replace Room #")
with revit.Transaction("Find / Replace Room # in View Names"):
    for view in views:
        try:
            changed = False

            title_param = view.get_Parameter(DB.BuiltInParameter.VIEW_DESCRIPTION)
            if title_param and not title_param.IsReadOnly:
                old_title = title_param.AsString()
                if old_title:
                    new_title = _renumber(old_title)
                    if new_title != old_title:
                        title_param.Set(new_title)
                        output.print_md("- Title: `{}` → `{}`".format(old_title, new_title))
                        changed = True

            name_param = view.get_Parameter(DB.BuiltInParameter.VIEW_NAME)
            if name_param and not name_param.IsReadOnly:
                old_name = view.Name
                new_name = _renumber(old_name)
                if new_name != old_name:
                    name_param.Set(new_name)
                    output.print_md("- Name: `{}` → `{}`".format(old_name, new_name))
                    changed = True

            if changed:
                renamed_count += 1
        except Exception as ex:
            errors.append((view.Id, str(ex)))

output.print_md("---")
output.print_md("Renamed **{}** view(s).".format(renamed_count))
if errors:
    output.print_md("**{} error(s):**".format(len(errors)))
    for vid, msg in errors:
        output.print_md("- {} — {}".format(output.linkify(vid), msg))
