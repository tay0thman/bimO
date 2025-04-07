# This script duplicates the selected elevation views and places them in the same location as the original views.
# The new views are named with an input prefix and the original view name.

# import pyRevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from Autodesk.Revit.DB import *

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

doc = __revit__.ActiveUIDocument.Document
elevationnames = []
# get the list of elevations views in the model
allviews = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
elevations = []
for view in allviews:
    if view.ViewType == ViewType.Elevation:
        elevations.append(view)
for elevation in elevations:
    elevationnames.append(elevation.Name)

# prompot the user to select the elevations to duplicate from the list
selected_elevations = forms.SelectFromList.show(elevationnames, button_name='Select Elevations', multiselect=True, title='Select Elevations to Duplicate')
# get the items from the list
selected_elevations = [elevations[elevationnames.index(elevation)] for elevation in selected_elevations]

# get the prefix for the new views
prefix = forms.ask_for_string(default='UG - ', Title='Enter Prefix for New Views')

# Get the list of available view templates
allviews = DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
viewtemplates = []
for view in allviews:
    if view.IsTemplate:
        # check if the viewtemplate is an elevation template
        if view.ViewType == ViewType.Elevation:
            viewtemplates.append(view)

# prompt the user to select the view template to use
viewtemplatesnames = []
for viewtemplate in viewtemplates:
    viewtemplatesnames.append(viewtemplate.Name)
selected_template_name = forms.SelectFromList.show(viewtemplatesnames, button_name='Select Template', multiselect=False, title='Select View Template to Use')
# get the selected view template
selected_template = viewtemplates[viewtemplatesnames.index(selected_template_name)]


# duplicate the selected elevations
with Transaction(doc, 'Duplicate Elevation Views') as t:
    t.Start()
    for elevation in selected_elevations:
        newviewID = elevation.Duplicate(ViewDuplicateOption.WithDetailing)
        newview = doc.GetElement(newviewID)
        newview.Name = prefix + elevation.Name
        #apply the selected view template to the new view
        newview.ViewTemplateId = selected_template.Id
    t.Commit()