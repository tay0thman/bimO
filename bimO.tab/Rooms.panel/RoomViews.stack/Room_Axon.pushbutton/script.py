# this script prompts the user to pick a room and then creates an axonometric view of the room
# the view is created by creating a 3D view and setting the view orientation to axonometric
# the view is then zoomed to the room and the view is named after the room

# import the Revit API
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
#import pyRevit
import pyrevit
from pyrevit import DB, UI, revit, HOST_APP
from pyrevit import script, forms, coreutils




__title__ = 'Room Axon'
__author__ = 'Tay Othman'
# get the active document
doc = __revit__.ActiveUIDocument.Document
activeview = doc.ActiveView

levelnames = []
# Get all the levels in the model
levels = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()


# get the level names
levelnames = []
for level in levels:
    levelnames.append(level.Name)

# prompt the user to select a level
selectedlevel = forms.SelectFromList.show(levelnames, button_name='Select Level', multiselect=False, title='Select Level', message='Select a level to filter rooms')
if selectedlevel == None:
    script.exit()
# get the index of the selectedlevel in the levelnames list
selectedlevelindex = levelnames.index(selectedlevel)

# get the level object from the levels list
selectedlevel = levels[selectedlevelindex]

# get all rooms in the model
rooms = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
# get all the bounding boxes of the rooms
for room in rooms:
    try:
        bb = room.get_BoundingBox(revit.doc.ActiveView)
        #print the volume of the bounding box
        
    except:
        print("Room <" + room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString() + "> has no bounding box")
        # filter out the room from the list
        rooms = [r for r in rooms if r != room]
        pass
#filter all the rooms on the selected level
rooms = [room for room in rooms if room.Level.Name == selectedlevel.Name]

#get list of room names
roomnames = []
roomnumbers = []
roomnamesandnumbers = []
for room in rooms:
    roomnames.append(room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())
    roomnumbers.append(room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString())
    roomnamesandnumbers.append(room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString())

# sort the roomnames list by room number
roomnamesandnumbers = [x for _, x in sorted(zip(roomnumbers, roomnamesandnumbers))]
rooms = [x for _, x in sorted(zip(roomnumbers, rooms))]
roomnumbers.sort()


# prompt the user to select a room
selectedroom = forms.SelectFromList.show(roomnamesandnumbers, button_name='Select Room', multiselect=True, title='Select Rooms', message='Select a room to create an axonometric view')

if selectedroom == None:
    script.exit()

# get the index of the selectedroom in the roomnames list
roomindex = []
for room in selectedroom:
    selectedroomindex = roomnamesandnumbers.index(room)
    roomindex.append(selectedroomindex)

# get the room object from the rooms list
selectedrooms = []
for index in roomindex:
    selectedrooms.append(rooms[index])

# get the list of all view templates
views_all = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
vfts_all = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType().ToElements()
templates_all, templates_3D, template_3D_names = [], [], []
for v in views_all:
    if v.IsTemplate:
        templates_all.append(v)
        if v.ViewType == DB.ViewType.ThreeD:
            templates_3D.append(v)
            template_3D_names.append(v.Name)
            
selectedtemplatename = forms.SelectFromList.show(template_3D_names, button_name='Select Template', multiselect=False, title='Select Template', message='Select a 3D view template to use')
if selectedtemplatename == None:
    script.exit()
# get the index of the selectedtemplatename in the template_3D_names list
selectedtemplateindex = template_3D_names.index(selectedtemplatename)
# get the template object from the templates_3D list
selectedtemplate = templates_3D[selectedtemplateindex]

# Get the list of all view types in the model
view3Dtypes = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType().ToElements()
# get the view type object for the 3D view using ViewFamily.ThreeDimensional
view3dtype = [v for v in view3Dtypes if v.ViewFamily == DB.ViewFamily.ThreeDimensional][0]


#####____________Determine if the view already exists____________#####


# Get the list of the 3d views in the model
views3D = DB.FilteredElementCollector(doc).OfClass(DB.View3D).WhereElementIsNotElementType().ToElements()
for room in selectedrooms:
    viewnamestring = "ROOM AXON _ " + room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
    for v in views3D:
        if v.Name == viewnamestring:
            print("View already exists <" + viewnamestring + "> is being recreated")
            #if the view is currently the active view navigate to the starting view
            if v.Id == activeview.Id:
                #get the starting view
                starting_view_id = DB.StartingViewSettings.GetStartingViewSettings(doc).ViewId
                starting_view = doc.GetElement(starting_view_id)
                #set the active view to the starting view
                HOST_APP.uidoc.RequestViewChange(starting_view)
                HOST_APP.uidoc.ActiveView = starting_view


views3Dlist = []
#####____________Transaction Start____________#####

with revit.Transaction('Create Room Axonometric Views'):
    #loop through the selected rooms

    
    for room in selectedrooms:
        viewnamestring = "ROOM AXON _ " + room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString() + " - " + room.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
        #Get the list of the 3d views in the model
        views3D = DB.FilteredElementCollector(doc).OfClass(DB.View3D).WhereElementIsNotElementType().ToElements()
        for v in views3D:
            if v.Name == viewnamestring:
                #if the view already exists delete the view
                doc.Delete(v.Id)
                                
        #create a 3D view
        view3d = DB.View3D.CreateIsometric(doc, view3dtype.Id)
        #get the bounding box of the room
        bb = room.get_BoundingBox(revit.doc.ActiveView)
        #adjust the section box to the bounding box of the room
        view3d.SetSectionBox(bb)
        #set the view name to the selected room name and numeber
        view3d.Name = viewnamestring
        #set the view scale to 1/4" = 1'-0"
        view3d.Scale = 48
        #set the view discipline to architectural
        view3d.Discipline = DB.ViewDiscipline.Architectural
        #set the view template to the selected template
        view3d.ViewTemplateId = selectedtemplate.Id
        # open the view in the active window
        views3Dlist.append(view3d)

for v in views3Dlist:
    #open the view in the active window
    UI.UIDocument.RequestViewChange(revit.uidoc, v)
    #set the active view to the view
    revit.uidoc.ActiveView = v






