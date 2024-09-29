# -*- coding: utf-8 -*-
__title__   = "Apply Filters to Templates"
__doc__     = """Version = 1.0
Date    = 09.17.2024
________________________________________________________________
Description:
Apply the selected view filters to multiple view templates
________________________________________________________________
How-To:
1. Select a view filter
2. Select multiple view templates to apply the filter to
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

#============================================ MAIN


viewfilters = DB.FilteredElementCollector(doc).OfClass(DB.ParameterFilterElement).ToElements()
viewfilternames = []
for viewfilter in viewfilters:
    viewfiltername = viewfilter.Name
    viewfilternames.append(viewfiltername)
viewfiltername = forms.SelectFromList.show(viewfilternames, button_name='Select View Filter', title='Select View Filter', multiselect=False)
if not viewfiltername:
    sys.exit()
viewfilter = viewfilters[viewfilternames.index(viewfiltername)]

color = forms.select_swatch(title='Select Color')
# convert color to RGB
rgb = (color.red, color.green, color.blue) # returns a tuple

red = rgb[0]
green = rgb[1]
blue = rgb[2]

rgb = DB.Color(red, green, blue)

# define override settings
override = DB.OverrideGraphicSettings()
override.SetCutLineColor(rgb)
override.SetProjectionLineColor(rgb)


selectviewtemplates = forms.select_viewtemplates(title='Select View Templates', button_name='Select View Templates', multiple=True)
Transaction = DB.Transaction(doc, 'Apply View Filter to Templates')
Transaction.Start()
for template in selectviewtemplates:
    try:
        template.AddFilter(viewfilter.Id)
        template.SetFilterOverrides(viewfilter.Id, override)
        print("Applied View Filter to: " + template.Name)
    except:
        print("Failed to apply View Filter to: " + template.Name)
        pass
Transaction.Commit()
