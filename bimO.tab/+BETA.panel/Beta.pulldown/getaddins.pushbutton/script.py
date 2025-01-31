# -*- coding: utf-8 -*-

#============================================ IMPORTS

#Revit API
import sys
from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
clr.AddReference('RevitAPI')
clr.AddReference('RevittAPIUI')
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

uiapp = Autodesk.Revit.UI.UIApplication.ActiveAddInId

print(uiapp)
