from pyrevit import script
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import HOST_APP
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import output
import sys
import os
output = script.get_output()

__title__ = 'Find Dim Overrides'
__author__  = 'Tay Othman, AIA'

# Prompt user to select an option (Active View or Entire Document)
ops = 'Active View', 'Entire Document'
formfilter = forms.CommandSwitchWindow.show(ops, message='Select an option:', title='Find Dim Overrides', exit=False)
if formfilter == 'Active View':
    ff = 0
    pass
elif formfilter == 'Entire Document':
    ff = 1
    pass

if ff == None:
    sys.exit()
elif ff == 1:
    # Get all the dimensions in the document
    doc = __revit__.ActiveUIDocument.Document
    collector = FilteredElementCollector(doc)
    dimCollector = collector.OfClass(Dimension)
    dimList = list(dimCollector)

elif ff == 0:
    # Get all the dimensions in the active view
    doc = __revit__.ActiveUIDocument.Document
    view = __revit__.ActiveUIDocument.ActiveGraphicalView
    collector = FilteredElementCollector(doc, view.Id)
    dimCollector = collector.OfClass(Dimension)
    dimList = list(dimCollector)

print('Total number of dimensions: ' + str(len(dimList)))

# enumerate through the list of dimensions and get the overrides
overriDIMs = []
for i, dim in enumerate(dimList):
    valtype = dim.ValueOverride
    if isinstance(valtype, str) and valtype != '':
        overriDIMs.append(dim)


print('Total number of dimensions with overrides: ' + str(len(overriDIMs)))
print('_________________________________________________________')
print('')
print('')
# define output styles
output.add_style('overriden {background-color: #ff0000; color: #ffffff; font-weight: bold;}')
output.add_style('truevalue {background-color: #f38b0b; color: #ffffff; font-weight: bold;}')


# display the overrides in a linkify format
if len(overriDIMs) > 0:
    # create a list of links
    linklist = []
    for dim in overriDIMs:
        linklist.append(dim)

    # create a linkify output window
for lnk in linklist:
    lnkOvv = lnk.ValueOverride
    lnkval = lnk.ValueString
    seperator = ' - overridden value: -'

    output.print_html('<truevalue>{}</truevalue>{}<overriden>{}</overriden>{}'.format(lnkval, seperator, lnkOvv, output.linkify(lnk.Id)))
