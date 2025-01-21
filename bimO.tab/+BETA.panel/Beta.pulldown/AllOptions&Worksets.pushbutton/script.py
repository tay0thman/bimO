
# -*- coding: utf-8 -*-

#============================================ IMPORTS

#Revit API
import sys
from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

#pyRevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

#============================================ VARIABLES
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

#============================================ FUNCTIONS




#query design options in the document
def get_design_options():
    design_options = DB.FilteredElementCollector(doc).OfClass(DesignOption).WhereElementIsNotElementType().ToElements()
    return design_options

#main
if __name__ == '__main__':
    design_options = get_design_options()
    for design_option in design_options:
        doElementfilter = DB.ElementDesignOptionFilter(design_option.Id)
        doObjects = FilteredElementCollector(doc).WherePasses(doElementfilter).ToElements()
        for d in doObjects:
            bb = d.get_BoundingBox(None)
            print (bb.Min, bb.Max)
        print (doObjects , design_option.Name)

# query worksets in the document
def get_worksets():
    worksets = DB.FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
    return worksets

view = doc.ActiveView
worksets = get_worksets()

#start transaction
t = Transaction(doc, 'show all worksets in view')
t.Start()
for ws in worksets:
    view.SetWorksetVisibility(ws.Id, DB.WorksetVisibility.Visible)
t.Commit()