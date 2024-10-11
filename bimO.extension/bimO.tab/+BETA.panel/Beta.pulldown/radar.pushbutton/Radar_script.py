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

#General Imports
import sys
import math

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

#============================================ HTML Styles
output = script.get_output()
output.add_style('bad {color:red; font-weight:bold;}')
output.add_style('warn {color:orange; font-weight:bold;}')
output.add_style('good {color:green; font-weight:bold;}')
output.add_style('cover {color:black; font-size:24pt; font-weight:bold;}')
output.add_style('header {color:black; font-size:18pt;}')
stringseperator = "_____________________________________________________________________________________________"
stringnewline = ""
#============================================ FUNCTIONS
class Get3DViewBoundingBox():
    def get_tempbbox(self, ToggleCAD, ToggleRVT, ToggleIFC, ToggleAll):
        violatingCAD = []
        violatingRVT = []
        badelements = []
        # Create a 3D view
        t = Transaction(doc, "Create 3D View")
        t.Start()
        view3Dtypes = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).WhereElementIsElementType().ToElements()
        view3dtype = [v for v in view3Dtypes if v.ViewFamily == DB.ViewFamily.ThreeDimensional][0]
        view = DB.View3D.CreateIsometric(doc, view3dtype.Id)
        worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
        for ws in worksets:
            view.SetWorksetVisibility(ws.Id, DB.WorksetVisibility.Visible)
        view.IsSectionBoxActive = True
        bb = view.GetSectionBox()
        if ToggleCAD:
            cads = FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
            if len(cads) == 0:
                print("No CAD Links in the model")
            else:
                for cad in cads:
                    cadbox = cad.get_BoundingBox(None)
                    cadmin = (cadbox.Min.X, cadbox.Min.Y, cadbox.Min.Z)
                    cadmax = (cadbox.Max.X, cadbox.Max.Y, cadbox.Max.Z)
                    if calculate_distance(cadmin, intOrig) > TenMiledistance or calculate_distance(cadmax, intOrig) > TenMiledistance:
                        violatingCAD.append(cad)
        if ToggleRVT:
            rvtlinks = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
            if len(rvtlinks) == 0:
                print("No RVT Links in the model")
            else:
                for rvt in rvtlinks:
                    rvtbox = rvt.get_BoundingBox(view)
                    rvtmin = (rvtbox.Min.X, rvtbox.Min.Y, rvtbox.Min.Z)
                    rvtmax = (rvtbox.Max.X, rvtbox.Max.Y, rvtbox.Max.Z)
                    if calculate_distance(rvtmin, intOrig) > TenMiledistance or calculate_distance(rvtmax, intOrig) > TenMiledistance:
                        violatingRVT.append(rvt)
        if ToggleIFC:
            pass
        allrvt = FilteredElementCollector(doc).OfClass(RevitLinkType).ToElements()
        allcad = FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
        if len(allrvt) > 0:
            view.HideElements(FilteredElementCollector(doc).OfClass(RevitLinkType).ToElementIds())
        if len(allcad) > 0:
            view.HideElements(FilteredElementCollector(doc).OfClass(ImportInstance).ToElementIds())
        view.IsSectionBoxActive = False
        view.IsSectionBoxActive = True
        bbh = view.GetSectionBox()
        if ToggleAll:
            elcollector = FilteredElementCollector(doc,view.Id).WhereElementIsNotElementType().ToElements()
            for el in elcollector:
                if el.get_BoundingBox(view) is not None and hasattr(el, 'Name') and hasattr(el, 'Category'):
                    bbox = el.get_BoundingBox(view)
                    if analyzebbox(bbox, intOrig) == 0:
                        badelements.append(el)

        t.Dispose()
        return bb, violatingCAD, violatingRVT, bbh, badelements
               
#____________________________________________ Calculate Distance
def calculate_distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

    return distance

#____________________________________________ Calculate Horizontal Distance
def calculate_Horizontal_Distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 )
    deltaX = (x2 - x1)
    deltaY = (y2 - y1)

    return distance, deltaX, deltaY
#____________________________________________ Get Bounding Box
def get_bounding_box(view):
    bb = view.CropBox
    min = bb.Min
    max = bb.Max
    return min, max

#____________________________________________ Get ProjectBase and Survey Points
def get_project_base_and_survey_points(doc):
    basept = DB.BasePoint.GetProjectBasePoint(doc).Position
    basept_tuple = (basept.X, basept.Y, basept.Z)
    survpt = DB.BasePoint.GetSurveyPoint(doc).Position
    survpt_tuple = (survpt.X, survpt.Y, survpt.Z)
    intOrig = (0,0,0)
    return basept_tuple, survpt_tuple, intOrig
#____________________________________________ GET DESIGN OPTIONS
def getalldesignoptionobjects(doc):
    dbobjs = []
    design_options = FilteredElementCollector(doc).OfClass(DesignOption).ToElements()
    for do in design_options:
        do_filter = ElementDesignOptionFilter(do.Id)
        x = FilteredElementCollector(doc).WherePasses(do_filter).ToElements()
        dbobjs.append(x)

    return design_options, dbobjs
#____________________________________________ ANALYZE BOUNDING BOX
def analyzebbox(bbox, intOrig):
    min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
    max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    if calculate_distance(min, intOrig) > TenMiledistance or calculate_distance(max, intOrig) > TenMiledistance:
        Status = 0
    else:
        Status = 1
    return Status

#=========================== MAIN

TestScore = 0
TenMiledistance = 52800 #Linear Feet
#__________________________________________check the distnaces of base and survey points
output.print_html('<cover>______:satellite_antenna:__Ten Mile Radar___________</cover>')
print(stringseperator)
print("")
output.print_html('<header>Checking model placement and coordinates</header>')
basept, survpt, intOrig = get_project_base_and_survey_points(doc)
surveydistance = calculate_distance(survpt, intOrig)
if surveydistance > TenMiledistance:
    output.print_html('<bad>!!............Survey Point is more than 10 miles away from the Internal Origin.</bad>')
else:
        output.print_html('<good>OK............Survey Point is less than 10 miles away from the Internal Origin.</good>')
baseptdistance = calculate_distance(basept, intOrig)
if baseptdistance > TenMiledistance:
    output.print_html('<bad>!!............Project Base Point is more than 10 miles away from the Internal Origin</bad>')

else:
        output.print_html('<good>OK............Project Base Point is less than 10 miles away from the Internal Origin.</good>')

# Print Distances
print (stringseperator)
print ("Internal Origin Coordinates = " + str(intOrig))
print ("Project Base Point Coordinates = " + str(basept))
print ("Survey Point Coordinates = " + str(survpt))
print("")
print (stringseperator)
print("")
print("")
print ("Project Base Point Distance from Internal Origin = " + str(baseptdistance))
print ("Survey Point Distance from Internal Origin = " + str(surveydistance))
print ("Project Base Point to Survey Delta X = " + str(calculate_Horizontal_Distance(basept, survpt)[1]))
print ("Project Base Point to Survey Delta Y = " + str(calculate_Horizontal_Distance(basept, survpt)[2]))
print ("Horizontal Distance between Project Base Point and Survey Point = " + str(calculate_distance(basept, survpt)))
ProjectElevation = survpt[2] - basept[2]
print ("Project Elevation = " + str(ProjectElevation))
print (stringseperator)
print("")
print("")

#__________________________________________Get the bounding box of the 3D view
output.print_html("<header>Checking the document's boundingbox extents </header>")
bbox_instance = Get3DViewBoundingBox()
bbox = bbox_instance.get_tempbbox(0,0,0,0)[0]
min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
print("")
print(stringseperator)
print("")
if calculate_distance(min, intOrig) > TenMiledistance or calculate_distance(max, intOrig) > TenMiledistance:
    output.print_html('<bad>!!............3D View Bounding Box extends more than 10 miles away from the Internal Origin</bad>')
else:
    output.print_html('<good>OK............3D View Bounding Box is located less than 10 miles away from the Internal Origin.</good>')
    TestScore += 1

#__________________________________________Get Objects in Design Options
print("")
print(stringseperator)
output.print_html("<header>Checking the design options objects</header>")
print(stringseperator)
design_option_objects = getalldesignoptionobjects(doc)
violating_design_option_objects = []
violating_options = []
for x in design_option_objects[1]:
    for y in x:
        dbbox = y.get_BoundingBox(None)
        dbmin = (dbbox.Min.X, dbbox.Min.Y, dbbox.Min.Z)
        dbmax = (dbbox.Max.X, dbbox.Max.Y, dbbox.Max.Z)
        if calculate_distance(dbmin, intOrig) > TenMiledistance or calculate_distance(dbmax, intOrig) > TenMiledistance:
            violating_design_option_objects.append(x)
            if y.DesignOption.Name not in violating_options:
                violating_options.append(y.DesignOption.Name)
if len(violating_design_option_objects) > 0:
    output.print_html('<bad>!!............Design Option Objects are located more than 10 miles away from the Internal Origin</bad>')
    for x in violating_design_option_objects:
        for y in x:
            print(output.linkify(y.Id), y.Name, " - Is part of design option - ", y.DesignOption.Name )
else:
    output.print_html('<good>OK............Design Option Objects are located less than 10 miles away from the Internal Origin.</good>')
    TestScore += 1
#__________________________________________Check Test Score
if TestScore >= 2:
    output.print_html('<good>OK............All Tests Passed.</good>')
    sys.exit()
else:
    output.print_html('<bad>!!............Distant objects detected, Proceeding with additional analysis</bad>')

#__________________________________________Check CAD and RVT Links
print(stringseperator)
output.print_html('<header>Checking CAD and RVT Links</header>')
print(stringseperator)
bboxLink = bbox_instance.get_tempbbox(1,1,1,0)
badcads = bboxLink[1]
badrvts = bboxLink[2]
cleanbbox = bboxLink[3]
# print (bboxLink[1], bboxLink[2])
# print(bbox.Min, cleanbbox.Min)
if len(badcads) > 0 or len(badrvts) > 0:
    for x in badcads:
        print(output.linkify(x.Id),"__" , x.Name, x.Category.Name)
    for x in badrvts:
        print(output.linkify(x.Id),"__" , x.Name, x.Category.Name)
else:
    output.print_html('<good>OK............All CAD and RVT Links are located less than 10 miles away from the Internal Origin.</good>')
    TestScore += 1
    print(stringseperator)
if analyzebbox(cleanbbox, intOrig) == 0:
    output.print_html('<warn>!!............Distant objects are still being detected!</warn>')
    output.print_html('<warn>!!............Further Analysis Required.</warn>')
else:
    output.print_html('<good>OK............All Objects are located less than 10 miles away from the Internal Origin.</good>')
    sys.exit()
print(stringseperator)
output.print_html('<header>Checking everything, It is going to take a while.</header>')
output.print_html('<header>please be patient.</header>')
#__________________________________________Check Bounding Box of Every Element in the Model
print(stringseperator)
getbadelements = bbox_instance.get_tempbbox(0,0,0,1)
badelements = getbadelements[4]
if len(badelements) > 0:
    output.print_html('<bad>!!............Elements below are located more than 10 miles away from the Internal Origin</bad>')
    for x in badelements:
        print(output.linkify(x.Id), x.Name, x.Category.Name)
else:
    output.print_html('<good>.........All Objects are located less than 10 miles away from the Internal Origin.</good>')
    TestScore += 1