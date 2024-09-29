# -*- coding: utf-8 -*-
__title__ = 'Create Views'
__author__  = 'Tay Othman, AIA'
__doc__ = """Create Cove.tool Views
            Author: Tay Othman, AIA"""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import pyrevit.DB as DB
import pyrevit


doc = DocumentManager.Instance.CurrentDBDocument

# create a 3D view using the default 3D view template
view = DB.View3D.CreateIsometric(doc, DB.ViewFamily.ThreeDimensional)
view_windows = "3D - cove.tool windows"

# Collect all the curtain panels that has a materials with the name contains glass or glazing
GlassCollector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
