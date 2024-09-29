from pyrevit import script
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import HOST_APP
from Autodesk.Revit.DB import *
from pyrevit import output
import sys
import math
import os
output = script.get_output()

__title__ = 'Find Project Coorindates'
__author__  = 'Tay Othman, AIA'

# Define a function to calculate the distance between two points
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

# Get the Active Document
doc = revit.doc

# Get the location of basepoint and survey point, and convert Revit's XYZ to a tuple
BasePoint = DB.BasePoint
basept = DB.BasePoint.GetProjectBasePoint(doc).Position
basept_tuple = (basept.X, basept.Y, basept.Z)
survpt = DB.BasePoint.GetSurveyPoint(doc).Position
survpt_tuple = (survpt.X, survpt.Y, survpt.Z)
active_project_location = doc.ActiveProjectLocation
intOrig = (0,0,0)

print ("Internal Origin Coordinates = " + str(intOrig))
print ("Project Base Point Coordinates = " + str(basept))
print ("Survey Point Coordinates = " + str(survpt))
print("")

# calculate distances

basedistance = calculate_distance(basept_tuple, intOrig)
surveydistance = calculate_distance(survpt_tuple, intOrig)
hdistance = calculate_Horizontal_Distance(survpt_tuple, basept_tuple)

# Print Distances
print ("__________________________________________________________________________________________")
print("")
print("")
print ("Project Base Point Distance from Internal Origin = " + str(basedistance))
print ("Survey Point Distance from Internal Origin = " + str(surveydistance))
print ("Project Base Point to Survey Delta X = " + str(calculate_DeltaXY(basept_tuple, survpt_tuple)[0]))
print ("Project Base Point to Survey Delta Y = " + str(calculate_DeltaXY(basept_tuple, survpt_tuple)[1]))

print ("Horizontal Distance between Project Base Point and Survey Point = " + str(hdistance))

ProjectElevation = survpt.Z - basept.Z
print ("Project Elevation = " + str(ProjectElevation))

# Get the Shared Coordinates
shared_coords_transform = active_project_location.GetTransform().Origin
print ("__________________________________________________________________________________________")
print("")
print("")
print("Shared Coordinates Transform:")
print(shared_coords_transform)
print("")
BasePointSharedPosition = DB.BasePoint.GetProjectBasePoint(doc).SharedPosition
print("")
print("BasePoint Shared Position:")
print(str(BasePointSharedPosition))

# Get the geographic location
ProjectLocation = doc.ActiveProjectLocation
projectPosition = ProjectLocation.GetProjectPosition(XYZ.Zero)
angleToTrueNorth = projectPosition.Angle
angle_in_degrees = math.degrees(angleToTrueNorth)

print ("__________________________________________________________________________________________")
print("")
print("")
print("Angle to True North:")
print(str(angle_in_degrees) + " degrees")