"""Select multiple sheets from a list"""
#pylint: disable=import-error,invalid-name
import os
import getpass
import random

import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms, revit
doc = __revit__.ActiveUIDocument.Document
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, Viewport, XYZ, TextNoteType

__title__ = 'Detail Numbering'
__author__  = 'Tay Othman, AIA'

# Get the active view
active_view = __revit__.ActiveUIDocument.ActiveView

# Get all viewports in the active view
viewports = FilteredElementCollector(active_view.Document, active_view.Id).OfClass(Viewport).ToElements()

# Print the list of viewports and their center coordinates
import math

#Tempoarly number the viewports to be X+autoincrement
for i, viewport in enumerate(viewports):
    view_id = viewport.ViewId
    view = doc.GetElement(view_id)
    ranindex = random.randint(1, 1000)
    # Set the VIEW_NAME and VIEW_DESCRIPTION properties
    with Transaction(doc, 'Set View Properties') as tx:
         tx.Start()
         xn = "Xx" + str(ranindex)
         view.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(xn)
         tx.Commit()
         break
    

# Create a list of the sheet domains (30" x 42")
xdomains = [(2.5, 3.1), (1.91, 2.5), (1.32, 1.91), (0.731, 1.32), (0, 0.731)]
ydomains = [(1.85, 2.5), (1.25, 1.85), (0.656, 1.25), (0, 0.731)]
    
# Create a list of 2D domains
domains_2d = []
for i in range(len(xdomains)):
      for j in range(len(ydomains)):
        domain = ((xdomains[i][0], xdomains[i][1]), (ydomains[j][0], ydomains[j][1]))
        domains_2d.append(domain)

# Get all viewports in the active view
viewports = FilteredElementCollector(active_view.Document, active_view.Id).OfClass(Viewport).ToElements()
# Change the VIEWPORT_DETAIL_NUMBER parameter of the viewports to match domains_2d based on their center coordinates
for i, viewport in enumerate(viewports):
    view_id = viewport.ViewId
    view = doc.GetElement(view_id)
    # Get the center coordinates of the viewport
    center = viewport.GetBoxCenter()
    outline = viewport.GetBoxOutline()
    lower_left = outline.MinimumPoint
    # Find the mid point between the lower left and the center of the viewport
    mid_point = XYZ((lower_left.X + center.X) / 2, (lower_left.Y + center.Y) / 2, 0)
    # Find a point between the lower left and the center of the viewport that is 1/4 of the distance from the lower left
    # This point will be used to determine the viewport's domain
    quarter_point = XYZ((lower_left.X + mid_point.X) / 2, (lower_left.Y + mid_point.Y) / 2, 0)

    # Find the corresponding domains_2d index that corresponds to the viewport's center
    for k, domain in enumerate(domains_2d):
        if quarter_point.X >= domain[0][0] and quarter_point.X <= domain[0][1] and quarter_point.Y >= domain[1][0] and quarter_point.Y <= domain[1][1]:
            detnum = str(k+1)  # add 1 to the
            print detnum + " - " + view.Name
            # Set the VIEWPORT_DETAIL_NUMBER parameter to the viewport
            with Transaction(doc, 'Set View Properties') as tx:
                tx.Start()
                view.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(detnum)
                tx.Commit()
            break

# Display a confirmation dialog box showing "Done Renaming All The Viewports of This Sheet"
forms.show_balloon("Done Renaming All The Viewports of This Sheet", "Done Renaming All The Viewports of This Sheet", "information")