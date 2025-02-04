#using RevitAPI + Python3
#find rooms that are not placed and delete them

import clr
# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *


uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
doc = uidoc.Document
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
not_placed_rooms = []
for room in all_rooms:
    if room.Location == None:
        not_placed_rooms.append(room)
if not_placed_rooms:
    with Transaction(doc,"Delete not placed rooms") as t:
        t.Start()
        for room in not_placed_rooms:
            doc.Delete(room.Id)
        t.Commit()