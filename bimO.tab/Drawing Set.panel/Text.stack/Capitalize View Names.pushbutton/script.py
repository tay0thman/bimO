
"""Select multiple sheets from a list"""
#pylint: disable=import-error,invalid-name
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms, revit
import sys
import os
appdata = str(os.getenv('APPDATA'))
print (appdata)
import clr
clr.AddReference('RevitAPI')
from System.Collections.Generic import List
from pyrevit import forms as frm

libpath = appdata + "\\pyRevit-Master\\extensions\\DES.extension\\lib"
sys.path.append(appdata + "\\pyRevit-Master\\extensions\\DES.extension\\lib")

import __telemetry as telemetry

__author__ = 'Tay Othman, AIA'

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document

# Get all views placed on sheets
views_on_sheets =  FilteredElementCollector(doc).OfClass(Viewport).ToElements()

# Create an empty list to store views with lowercase letters in their names
views_with_lowercase = []
Viewnames = []
ViewIDS = []

# Loop through all views on sheets and find views with at least one lower case letter in their names and append it to the list
for view in views_on_sheets:
    viewId = doc.GetElement(view.ViewId)
    viewname = viewId.Name
    if any(c.islower() for c in viewname):
        views_with_lowercase.append(view)
        ViewIDS.append(view.Id)
        Viewnames.append(viewname)
        

# Display a checklist form with all the view names and a checkbox to filter the list
selected_views = frm.SelectFromList.show(Viewnames, button_name='Capitalize!!', multiselect=True, checked_only=True)
if selected_views:
    # Filter the list of views based on the selected views
    filtered_views = [view for view in views_on_sheets if doc.GetElement(view.ViewId).Name in selected_views]
else:
    sys.exit()
# Loop through the filtered views and capitalize their names
for view in filtered_views:
    view_name = doc.GetElement(view.ViewId).Name
    view_name_upper = view_name.upper()
    print(view_name + " >>>>>>>>> " + view_name_upper)
    with Transaction(doc, 'Set Capitalized Name') as tx:
        tx.Start()
        view.get_Parameter(BuiltInParameter.VIEW_NAME).Set(view_name_upper)
        tx.Commit()
    

# Show a message box indicating the number of views that were capitalized
forms.alert("Capitalized the names of {} views.".format(len(filtered_views)))


