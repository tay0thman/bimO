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

from Autodesk.Revit.DB import Line, Transaction

# Create an empty list to store graphics styles
tiposdelineas = []

# Start a transaction
trline = Transaction(doc, "LINETEMP")
trline.Start()
# create a sketch plane on the internal origin
sketchPlane = SketchPlane.Create(doc, Plane.CreateByNormalAndOrigin(XYZ(0, 0, 1), XYZ(0, 0, 0)))

# Create a detail curve
modelcurve = doc.Create.NewModelCurve(Line.CreateBound(XYZ(0, 0, 0), XYZ(10, 0, 0)), sketchPlane)

# Iterate through line styles and add them to the list
for gsid in modelcurve.GetLineStyleIds():
    gs = doc.GetElement(gsid)
    tiposdelineas.append(gs)
    print(gs.Name)
OUT = tiposdelineas
# Roll back the transaction (since we don't want to make any changes)
trline.RollBack()


