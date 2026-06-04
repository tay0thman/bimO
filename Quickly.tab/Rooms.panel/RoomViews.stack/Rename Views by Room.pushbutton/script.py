# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Rename selected views to follow the closest room.

For each view the user picks, find the room whose location point is closest to
the view's crop-box centroid. If the view name contains a letter-prefixed
3-digit number (e.g. "A101"), replace those 3 digits with the room's `Number`.

Views without a crop box (or with no rooms visible) are skipped with a notice.
"""
import re

from pyrevit import revit, DB, forms, script

__title__ = "Rename Views\nby Room"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

# Match a letter followed by exactly 3 digits — e.g. "A101", "P204b" → "P204"
_LETTER_3DIGIT = re.compile(r"([A-Za-z])(\d{3})")

doc = revit.doc


def _get_closest_room_number(view):
    """Return the Number of the room nearest the view's crop-box center, or None."""
    crop = view.CropBox
    if not crop:
        return None
    centroid = (crop.Max + crop.Min) / 2
    centroid_2d = DB.XYZ(centroid.X, centroid.Y, 0)

    rooms_in_view = (DB.FilteredElementCollector(doc, view.Id)
                     .OfCategory(DB.BuiltInCategory.OST_Rooms)
                     .WhereElementIsNotElementType()
                     .ToElements())

    closest = None
    closest_distance = None
    for room in rooms_in_view:
        if not room.Location or not room.Number:
            continue
        room_pt = room.Location.Point
        room_2d = DB.XYZ(room_pt.X, room_pt.Y, 0)
        distance = room_2d.DistanceTo(centroid_2d)
        if closest_distance is None or distance < closest_distance:
            closest = room
            closest_distance = distance
    return closest.Number if closest else None


def _replace_letter_3digit(name, new_number):
    """Replace the first letter+3-digit pattern in name with letter+new_number."""
    return _LETTER_3DIGIT.sub(lambda m: m.group(1) + new_number, name, count=1)


views_to_rename = forms.select_views(
    button_name="Rename Selected",
    use_selection=True,
    multiple=True,
)
if not views_to_rename:
    script.exit()

skipped = []
renamed = []

with revit.Transaction("Rename Views by Closest Room"):
    for view in views_to_rename:
        room_number = _get_closest_room_number(view)
        if not room_number:
            skipped.append((view.Name, "no crop box / no rooms in view"))
            continue
        old_name = view.Name
        new_name = _replace_letter_3digit(old_name, room_number)
        if new_name == old_name:
            skipped.append((old_name, "no letter+3-digit pattern in name"))
            continue
        try:
            view.Name = new_name
            renamed.append((old_name, new_name))
        except Exception as ex:
            skipped.append((old_name, str(ex)))

output = script.get_output()
output.print_md("### Rename Views by Room")
output.print_md("**Renamed: {}**".format(len(renamed)))
for old, new in renamed:
    output.print_md("- `{}` → `{}`".format(old, new))
if skipped:
    output.print_md("\n**Skipped: {}**".format(len(skipped)))
    for name, reason in skipped:
        output.print_md("- `{}` — {}".format(name, reason))
