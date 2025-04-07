"""Select Multiple Grids and turn off the bubble visibility on one side and turn on the bubble visibility on the other side"""
#pylint: disable=import-error,invalid-name
__title__ = 'Flip Grids'
__author__  = 'Tay Othman, AIA'

from Autodesk.Revit.DB import *
from pyrevit import forms, revit, DB
import os
import getpass
from datetime import datetime
import os
import sys

# Set the active Revit application and document
doc = revit.doc
active_view = doc.ActiveView
# Select multiple objects
objects = revit.get_selection()
# filter the grids of the selection
grids = [obj for obj in objects if isinstance(obj, DB.Grid)]

# Check if grids are selected
if not grids:
    forms.alert('No Grids selected!', exitscript=True)
end_0 = []
end_1 = []
# Enumerate through the selected grids
with revit.Transaction('Flip Grids'):
    for grid in grids:
        # Define Ends
        end_0 = grid.IsBubbleVisibleInView(DB.DatumEnds.End0, active_view)
        end_1 = grid.IsBubbleVisibleInView(DB.DatumEnds.End1, active_view)

        if end_0:
            grid.HideBubbleInView(DB.DatumEnds.End0, active_view)
        else:
            grid.ShowBubbleInView(DB.DatumEnds.End0, active_view)

        if end_1:
            grid.HideBubbleInView(DB.DatumEnds.End1, active_view)
        else:
            grid.ShowBubbleInView(DB.DatumEnds.End1, active_view)


