from pyrevit import script
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import HOST_APP
from Autodesk.Revit.DB import *
from pyrevit import output
import sys
import math
import os

import pyrevit
output = script.get_output()

__title__ = 'Find Link Coorindates'
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
maindoc = revit.doc
#query the list of links in the model, make sure only loaded links are visible
link_instances = DB.FilteredElementCollector(maindoc).OfClass(DB.RevitLinkInstance).ToElements()

# Get the Loaded Revit Links from the list
link_instances = [link for link in link_instances if link.IsValidObject and link.CanBeHidden]

# Add a Header Style
output.add_style('Header {color: #4a4a4a; font-weight: bold; font-size: 24px; underline: True;}')



# Prompt the user to select a link from the list
link = forms.SelectFromList.show(link_instances, button_name='Select Link', multiselect=True, name_attr='Name', button_exit_name='Cancel')
if not link:
    sys.exit()

#Iterate through the list of selected links
for link in link:
    # Get the Link Document
    doc = link.GetLinkDocument()
    # Print the Link's Name
    print ("__________________________________________________________________________________________")
    print("")
    print("")
    link_name = str(link.Name)
    # remove any "<" or ">" characters from the link name
    link_name = link_name.replace("<", "")
    link_name = link_name.replace(">", "")
    output.print_html('<Header>Link Name: {}</Header>'.format(link_name))
    print("")
    print ("__________________________________________________________________________________________")

    # Get the location of basepoint and survey point, and convert Revit's Link XYZ to a tuple
    BasePoint = DB.BasePoint
    # Get the base point and survey point of the selected
    try:
        basept = DB.BasePoint.GetProjectBasePoint(doc).Position
    except:
        print("Link Cannot be Analyzed, Link is not Loaded")
        # skip to the next link
        continue

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
    print("")
    print("")
    print ("__________________________________________________________________________________________")
    continue
print ("End of Report")