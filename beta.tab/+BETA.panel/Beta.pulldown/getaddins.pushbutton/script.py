# -*- coding: utf-8 -*-

#============================================ IMPORTS


#.NET Imports
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
from pyrevit import revit, DB, UI

loaded_apps = []
for app in __revit__.LoadedApplications:
    loaded_apps.append(app)

sorted_apps = sorted(loaded_apps, key=lambda x: x.GetType().FullName)
for app in sorted_apps:
    print(app.GetType().FullName)

