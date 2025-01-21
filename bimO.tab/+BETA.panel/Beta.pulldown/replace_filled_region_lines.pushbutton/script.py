#using RevitAPI + Python3
#get a list of a filled region element and change the line style of the sketch lines

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
from Autodesk.Revit.DB.Analysis import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
import Autodesk.Revit.UI.Selection as selection


uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
doc = uidoc.Document
# variables
filled_regions = []
innersketchelements = []
outtersketchelements = []
elementId = ElementId(-2000285)
print(elementId)
print(doc.GetElement(elementId))
innerlinestyle = doc.GetElement(elementId)
outerlinestyle = doc.GetElement(elementId)
linestyleparam = DB.BuiltInParameter.BUILDING_CURVE_GSTYLE
# get the filled region element
selection = uidoc.Selection.GetElementIds()

T = Transaction(doc, "Change line style")
T.Start()

# get the filled region element
for elementid in selection:
    element = doc.GetElement(elementid)
    print(element)
  
    # get the sketch elements of the filled region
    elementFilter = DB.ElementCategoryFilter(BuiltInCategory.OST_SketchLines)
    sketchId = element.GetDependentElements(elementFilter)
    for id in sketchId:
        sketch = doc.GetElement(id)
        param = sketch.LineStyle
        # set the value of linestyleparam to the sketch element
        sketch.LineStyle = innerlinestyle
        print(sketch.LineStyle)

#shake the filled region
for elementid in selection:
    element = doc.GetElement(elementid)
    filled_regions.append(element)
    for fregion in filled_regions:
        fregion.Location.Move(DB.XYZ(0.1, 0, 0))
        fregion.Location.Move(DB.XYZ(-0.1, 0, 0))
        print('Shaking Filled Regions in: {}'.format(fregion))

T.Commit()


