# This script prompts the user to select a room and then select the list of the doors within the rooms.
# this script uses Revit's TO Room and FROM Room parameters to get the doors that are within the selected room.
# The script then creates a new list of the doors that are within the selected room.
# This script uses Cpython and Pyrevit to run the script in Revit.

import pyrevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
from pyrevit import HOST_APP

__title__ = 'Doors From Rooms'
__author__ = 'Tay Othman'
__doc__ = 'This script prompts the user to select a room and then select the list of the doors within the rooms.'



# filter the list of doors that has the selected room as the FROM Room.id and add them to the list of doors that are within the room
def get_doors_from_room(room):
    doors = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    # get all the door instances in the model
    roomdoors = []
    for door in doors:
        if door.FromRoom[0].Id == roomid:
            roomdoors.append(door)


def Roomlist():
    Roomlist = []
    for room in rooms:
        Roomlist.append(room.LookupParameter('Number').AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
    return Roomlist


# get all the rooms in the model
rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

# Get the Room Name and Number
ops = {}
roomnames = []
roomnumbers = []
roomstrings = []
roomtodoors = []
roomfromdoors = []

# sort the list of rooms by numerical order
roomsort = sorted(rooms, key=lambda x: x.LookupParameter('Number').AsString())
# build the list of room names and numbers
for room in roomsort:
    roomnames.append(room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
    roomnumbers.append(room.LookupParameter('Number').AsString())
    roomstrings.append(room.LookupParameter('Number').AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())

# prompt the user to select a room and return the index of the room string
selection = forms.SelectFromList.show(roomstrings, button_name='Select Room', title='Select Room', multiselect=False)

# find the index of the selected room
roomindex = roomstrings.index(selection)

# get the room object from the index
room = roomsort[roomindex]
# get the room.id from the selected room
roomid = room.Id

#find the doors that have the value of roomid in the FROM Room parameter
roomdoors = get_doors_from_room(room)




