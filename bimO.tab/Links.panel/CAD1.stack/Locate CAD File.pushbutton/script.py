#This script uses python and Revit API to locate the cad file of the selected element
# Using pyrevit libraries
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ImportInstance
# import pyrevit forms
from pyrevit import script
from pyrevit import forms
from pyrevit import revit
from pyrevit import DB
from pyrevit import HOST_APP

import os


# get the current document
doc = __revit__.ActiveUIDocument.Document
output = script.get_output()

# get the selection
selection = revit.get_selection()

# check if there is a selection
if selection:
    # get the first element of the selection
    selected_element = selection[0]
    # check if the selected element is a dwg link
    if selected_element.IsLinked:
        # get the cad file name
        cad_file_name = selected_element.get_Parameter(BuiltInParameter.IMPORT_SYMBOL_NAME).AsString()
        # get the cad file path
        
        # print the cad file name and path
        print('CAD File Name: ' + cad_file_name)
        # using windows explorer to open the folder containing the cad file
        os.startfile(os.path.dirname(cad_file_path))
    else:
        forms.alert('Please select a CAD link', exitscript=True)
else:
    forms.alert('Please select an element', exitscript=True)


