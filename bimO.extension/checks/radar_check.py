# -*- coding: utf-8 -*-
__title__   = "10 Mile Radar"
__doc__     = """Version = 1.0
Date    = 09.17.2024
________________________________________________________________
Description:
Get the bounding box of the document by creating a default 3D view and calculate the view's bounding box
________________________________________________________________
How-To:
1. run the script
2. create a 3D view
3. the script will calculate the bounding box of the view
________________________________________________________________
TODO:
[FEATURE] - 1- Pending user feedback
[FEATURE] - 2- Pending Revit API Updates
________________________________________________________________
Last Updates:
- [09.16.2024] v0.1 Initial Prototype
________________________________________________________________
Author: Tay Othman"""

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
def get_bounding_box(view):
    bb = view.CropBox
    min = bb.Min
    max = bb.Max
    return min, max

def create_3d_view():

    view = DB.View3D.CreateIsometric(doc, DB.View3D.CreateIsometric(doc, View3D.Id))
    return view
#============================================ MAIN

if __name__ == '__main__':
    view = create_3d_view()
    min, max = get_bounding_box(view)
    print(min, max)