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
#python imports
import math

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
from pyrevit import revit, DB, forms, script, HOST_APP, coreutils

#============================================  WORK VARIABLES
app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
BasePoint = DB.BasePoint
originpt = DB.XYZ(0,0,0)
originpt_tuple = (0,0,0)
basept = DB.BasePoint.GetProjectBasePoint(doc).Position
basept_tuple = (basept.X, basept.Y, basept.Z)
survpt = DB.BasePoint.GetSurveyPoint(doc).Position
survpt_tuple = (survpt.X, survpt.Y, survpt.Z)
active_project_location = doc.ActiveProjectLocation
intOrig = (0,0,0)
appunits = doc.GetUnits().GetFormatOptions(SpecTypeId.Length).GetUnitTypeId()
if (UnitTypeId.FeetFractionalInches).TypeId == appunits.TypeId:
    print ("System Units = Imperial Feet and Inches")

#============================================ FUNCTIONS
def get_bounding_box(view):
    bb = view.GetSectionBox()
    bb.Enabled = True
    bbox = bb.Bounds
    min = bbox[0]
    max = bbox[1]
    return bb, min, max

def create_3d_view():
    # Get the list of all view types in the model
    view3Dtypes = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType().ToElements()
    # get the view type object for the 3D view using ViewFamily.ThreeDimensional
    view3dtype = [v for v in view3Dtypes if v.ViewFamily == DB.ViewFamily.ThreeDimensional][0]
    view = DB.View3D.CreateIsometric(doc, view3dtype.Id)
    # enable the section box
    view.IsSectionBoxActive = True
    return view

def calculate_distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

    return distance


def calculate_Horizontal_Distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 )

    return distance


def calculate_DeltaXY(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the distance using the Euclidean distance formula
    deltaX = (x2 - x1)
    deltaY = (y2 - y1)

    return deltaX , deltaY

def determine_units():
    if appunits.TypeId == (UnitTypeId.FeetFractionalInches).TypeId:
        return "Imperial"
    else:
        return "Metric"

def getalldesignoptionobjects():
    designoptionobjects = []
    designoptions = FilteredElementCollector(doc).OfClass(DesignOption).ToElements()
    if designoptions:
        for do in designoptions:
            #get all objects in the design option
            designoptionobjects.append(do.GetDependentElements(ElementFilter()))
            print(do.GetGeneratingElementIds())

        return designoptionobjects
    else:
        return None





#============================================ MAIN


#__________________________________________________________________Build the Radar Box
# create a 3D view
# ceate a transaction
t = Transaction(doc, 'Create 3D View')
t.Start()
# get all design option Objects
dobjects = getalldesignoptionobjects()
if dobjects:
    for do in dobjects:
        print(do.Min, do.Max)
tempview = create_3d_view()
tempview
tempbbox = get_bounding_box(tempview)
t.Dispose # cancel the transaction


pt1 = (tempbbox[1].X, tempbbox[1].Y, tempbbox[1].Z)
pt2 = (tempbbox[2].X, tempbbox[2].Y, tempbbox[2].Z)

# calculate distances
dis1 = calculate_distance(pt1, originpt_tuple)
dis2 = calculate_distance(pt2, originpt_tuple)

# # Debug Print Distances
# print ("__________________________________________________________________________________________")
# print("")
# print("point 1 = " + str(pt1))
# print("point 2 = " + str(pt2))
# print("")
# print ("Min Point Distance from Internal Origin = " + str(minpt_distance))
# print ("Max Point Distance from Internal Origin = " + str(maxpt_distance))

if dis1 > 5280 or dis2 > 5280:
    print ("The Radar Box is larger than 10 miles, Additional Analysis Required")
    sys.exit()
else:
    print ("The Radar Box is within 10 miles")
    print ("Min Point Distance from Internal Origin = " + str(dis1))
    print ("Max Point Distance from Internal Origin = " + str(dis2))
    print ("Project Base Point to Survey Delta X = " + str(calculate_DeltaXY(pt1, pt2)[0]))
    print ("Project Base Point to Survey Delta Y = " + str(calculate_DeltaXY(pt1, pt2)[1]))
    print ("System Units = " + determine_units())
    print ("__________________________________________________________________________________________")
    print("")