# Load the Python Standard and DesignScript Libraries

from os import name
from unicodedata import category
import clr

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Analysis import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
import Autodesk.Revit.UI.Selection as selection
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import System
from System.Collections.Generic import *

uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
doc = uidoc.Document
document = DB.Document

# Get the list of all design options in the project
options = FilteredElementCollector(doc).OfClass(DesignOption).ToElements()

#Get the list if all Worksets in the project
worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()

#Get the list of all views in the project
views = FilteredElementCollector(doc).OfClass(View).ToElements()

# Get the list of unplaced schedules in the project
# schedules = FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements()
# for s in schedules:
#     if DB.View.GetPlacementOnSheetStatus(doc, s.Id) == PlacementType.Unplaced:
#         unplaced_schedules.append(s)
#         print(s.Name)

#Get the list of all Sheets in the project
sheets = FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()

#Get the list of all CAD imports in the project
cad_imports = []
options = FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
for i in options:
    if i.IsLinked:
        pass
    else:
        cad_imports.append(i)

#Get the list of all CAD links in the project
cad_links = FilteredElementCollector(doc).OfClass(CADLinkType).ToElements()

#Get the list of all linked models in the project
linked_models = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

# Get the list of all family class items that doesn't have a placed instance in the project
unplacedfamilies = []
families = FilteredElementCollector(doc).OfClass(Family).ToElements()
for f in families:
    placement = (f.FamilyPlacementType.ToString())
    cats = f.FamilyCategory.Name
    name = f.Name
    print(cats + ">>" + name)
    if f.IsUserCreated and f.CanBeHidden and cats != "Title Blocks" and cats != "Profiles" and cats != "Curtain Wall Mullions" and cats != "Level Heads" and cats != "View Titles" and cats != "Revision Cloud Tags" and cats != "Revision Clouds" and cats != "Revision Tags" and cats != "Grids" and cats != "Spot Elevations" and cats != "Spot Coordinates" and cats != "Spot Slopes" and cats != "Spot Elev Symbols" and cats != "Callout Heads" and cats != "Spot Slope Symbols" and cats != "Section Marks" and cats != "Section Heads" and cats != "Section Tail Symbols" and cats != "Section Boxes" and cats != "Section Lines" and cats != "Section Views" and cats != "Level Heads":
        x = f.GetDependentElements(None)
        instances = 0
        for y in x:
            if "FamilyInstance" in (str(doc.GetElement(y))):
                instances += 1
        if instances == 0:
            unplacedfamilies.append(f)
    else:
        pass

print(len(unplacedfamilies))








