# this script duplicates the linetype of the selected line element and prompst the user to select color, pattern and wieght for the new linetype
# The new linetype is then added to the project and the selected line elements are changed to the new linetype

# import Revit API
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

from pyrevit import revit, DB, forms
from pyrevit import script
from pyrevit import coreutils

# get selected elements
selected_elements = revit.get_selection()
if not selected_elements:
    # select elements if none are selected
    selected_elements = revit.pick_element_by_category(BuiltInCategory.OST_Lines)
    if not selected_elements:
        script.exit()


# get the linetype of the first item selected in the list
linetype = DB.ElementId(DB.Line.GetLineType(selected_elements[0].Document, selected_elements[0].GetTypeId()))

stylename = linetype.Name
stylepattern = linetype.GetCompoundStructure().GetLayers()[0].Function.ToString()
stylecolor = linetype.GetCompoundStructure().GetLayers()[0].Color

print(stylecolor, stylepattern, stylename)