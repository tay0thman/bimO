from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import UI

import clr
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import List

class RoomListItem(forms.TemplateListItem):
    @property
    def name(self):
        return self.item.GetParameters('Number')[0].AsString() + ' - ' + self.item.GetParameters('Name')[0].AsString()


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
active_view = doc.ActiveView
# Get the list of rooms in the model
rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
roomnames = [RoomListItem(room) for room in rooms]
selected_rooms = forms.SelectFromList.show(roomnames, 
                                            title='Select Rooms',
                                            button_name='Select Rooms', 
                                            multiselect=True)
if selected_rooms is None:
                                                script.exit()

# print the list of selected rooms
roomnumbers = [room.LookupParameter('Number').AsString() for room in selected_rooms]
# select the rooms
uidoc.Selection.SetElementIds(List[DB.ElementId]([room.Id for room in selected_rooms]))
