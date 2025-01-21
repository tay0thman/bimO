# -*- coding: utf-8 -*-
__title__   = "Sync Link Graphics"
__doc__     = """Version = 1.0
Date    = 09.09.2024
________________________________________________________________
Description:
Colorize a selected revit link in a selected view template
________________________________________________________________
How-To:
1. Select a Revit Link to transfer overrides
2. Select a source view template to use as a reference
3. Select multiple view templates to apply the overrides to
________________________________________________________________
TODO:
[FEATURE] - 1- Pending user feedback
[FEATURE] - 2- Pending Revit API Updates
________________________________________________________________
Last Updates:
- [09.09.2024] v0.1 Initial Prototype
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

# prompt user to select a Revit Link
linknames = []
linkcollector = FilteredElementCollector(doc).OfClass(RevitLinkType).ToElements()
for link in linkcollector:
    linkname = link.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    linknames.append(linkname)
link = forms.SelectFromList.show(linknames, button_name='Select Revit Link To Override', title='Select Revit Link', multiselect=False)
if not link:
    sys.exit()

# Get the index of the selected link
linkindex = linknames.index(link)
selection = linkcollector[linkindex]



# prompt user to select a view template
viewtemplate = forms.select_viewtemplates(title='Select Source View Template', button_name='Select View Template',multiple=False)
if not viewtemplate:
    sys.exit()


templateID = viewtemplate.Id
linkID = selection.Id
vt = doc.GetElement(templateID)
viewsource = doc.ActiveView

viewtemplates = forms.select_viewtemplates(title='Select View Template', button_name='Select View Template')
if not viewtemplates:
    sys.exit()

Transaction = DB.Transaction(doc, 'Update Overrides')
Transaction.Start()
link_settings = RevitLinkGraphicsSettings()
link_settings.LinkVisibilityType = LinkVisibility.Custom
link_settings.LinkedViewId = templateID
ls = vt.GetLinkOverrides(linkID)
print(ls)
# prompt user to select a view template
for view in viewtemplates:
    try:
        view.SetLinkOverrides(linkID, ls)
        print(view.Name , '-----------Link Colorized')
    except:
        view.SetLinkOverrides(linkID, ls)
        print(view.Name , '-----------Link Failed')
Transaction.Commit()

