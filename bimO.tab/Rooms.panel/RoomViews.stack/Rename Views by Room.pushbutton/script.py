"""Rename Views by Room Number"""
#pylint: disable=import-error,invalid-name
from ast import Name, Pass
from hmac import new
from math import ceil
from operator import contains
from pydoc import doc
import re
from pyrevit import forms, revit, DB, script

__title__ = 'Rename Views by Room'
__author__  = 'Tay Othman, AIA'

doc = revit.doc

# Get the active view
activeview = doc.ActiveView

# Get the view to process
view = activeview

def get_closest_room_number(view):
    # collect all the rooms visible in the view
    rooms = []
    viewcropbox = view.CropBox
    # get the center of the view
    if viewcropbox:
        viewcentroid = (viewcropbox.Max + viewcropbox.Min) / 2
        # Remove the Z value
        viewcentroid = DB.XYZ(viewcentroid.X, viewcentroid.Y, 0)
        # collect all the rooms visible in the view
        
    else:
        return None
    
    rooms = DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

    roomdistances = []
    for room in rooms:
        roomboundary = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
        if roomboundary:
            # get the centroid of the room
            roomname = room.Number
            # get room location point in 2D space
            roomlocation = room.Location.Point
            roomlocation = DB.XYZ(roomlocation.X, roomlocation.Y, 0)
            # get the distance between the room and the view center
            distance = roomlocation.DistanceTo(viewcentroid)
            roomdistances.append(distance)
        else:
            pass

    # Create a dictionary of rooms and distances
    roomdistancedict = dict(zip(rooms, roomdistances))

    # Sort the dictionary by distance
    sortedroomsbydistance = sorted(roomdistancedict.items(), key=lambda x: x[1])

    # Get the room with the smallest distance
    if len(sortedroomsbydistance) != 0:
        room = sortedroomsbydistance[0][0]
        return room.Number
    

# define a function to look for a three digit number in a string and replace it with a new 3 digit input
def replace_number(string, new_number):
    # find the first instance of a 3 digit number in the string
    for i in range(len(string)):
        if i+3 <= len(string) and string[i].isalpha() and string[i+1].isdigit() and string[i+2].isdigit() and string[i+3].isdigit():
            # replace the number with the new number
            # split the string into 3 parts
            part1 = string[:i+1]
            part2 = string[i+1:i+4]
            part3 = string[i+4:]
            # replace the number
            newstring = part1 + str(new_number) + part3
            return newstring


viewtorename = []
# Get all views plans in the project
viewscollector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
#determine if the view is a plan view
for view in viewscollector:
    if view.ViewType == DB.ViewType.FloorPlan:
        viewtorename.append(view)

# determine if the view is an elevation view
for view in viewscollector:
    if view.ViewType == DB.ViewType.Elevation:
        viewtorename.append(view)

#determine if the view is a section view
for view in viewscollector:
    if view.ViewType == DB.ViewType.Section:
        viewtorename.append(view)

#determine if the view is a 3D view
for view in viewscollector:
    if view.ViewType == DB.ViewType.ThreeD:
        viewtorename.append(view)


# List views to select
viewstoselect = forms.select_views(button_name='Select Views to Rename', multiple=True)

# loop through the selected views, find the closest room number
for view in viewstoselect:
    roomnumber = get_closest_room_number(view)
    print("View: ", view.Name, "Contains Room Number: ", roomnumber)
    # rename the view with the room number
    # viewname = view.Name
    # newviewname = replace_number(viewname, roomnumber)
    # # rename the view
    # print('View ' , viewname , ' renamed to ' , newviewname)