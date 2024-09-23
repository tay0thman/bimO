#using RevitAPI + Python3
#get a list of a filled region element and change the line style of the sketch lines

from calendar import c
import clr
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import BuiltInParameter, ElementId  # Add this import statement
from Autodesk.Revit.DB import WallUtils
import Autodesk.Revit.UI as RevitUI
from Autodesk.Revit.DB import Transaction  # Add this import statement


class LineStyleFinder:
    def __init__(self, uidoc):
        self.uidoc = uidoc
        self.doc = uidoc.Document

    def get_selected_element_ids(self):
        selection = self.uidoc.Selection.GetElementIds()
        return selection

    def get_graphical_style_id(self, element_id):
        element = self.doc.GetElement(element_id)
        param_id = DB.ElementId(BuiltInParameter.BUILDING_CURVE_GSTYLE)
        param_provider = DB.ParameterValueProvider(param_id)
        graphicalstyle = element.get_Parameter(BuiltInParameter.BUILDING_CURVE_GSTYLE)
        graphicalstyle_id = graphicalstyle.AsElementId()
        return graphicalstyle_id

# Usage example:
if __name__ == '__main__':
    uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
    line_style_modifier = LineStyleFinder(uidoc)
    selected_element_ids = line_style_modifier.get_selected_element_ids()
    for element_id in selected_element_ids:
        graphical_style_id = line_style_modifier.get_graphical_style_id(element_id)
        # Do something with the graphical style id
        print(graphical_style_id)
