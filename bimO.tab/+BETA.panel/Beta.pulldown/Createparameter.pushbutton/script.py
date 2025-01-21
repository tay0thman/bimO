# -*- coding: utf-8 -*-

import System
from System import Enum
from pyrevit import forms, script, DB, revit
from pyrevit import HOST_APP
from pyrevit import output
import sys
import os
import pyrevit.revit.db.create
output = script.get_output()
import pyrevit.revit.db

__title__ = 'Create Room Parameter'
__author__  = 'Tay Othman, AIA'
app = __revit__.Application
doc = revit.doc

parametertoadd = "Old Room Number"
parametertype = "Text"
parametervisibility = "Instance"

# Get all categories and built-in parameter groups
all_categories = [category for category in doc.Settings.Categories]
built_in_parameter_groups = [group for group in System.Enum.GetValues(DB.BuiltInParameterGroup)]
built_in_parameter_group_names = [DB.LabelUtils.GetLabelFor(n) for n in built_in_parameter_groups]

with revit.Transaction('Create Room Parameter'):
    # create a categry set
    category_set = app.Create.NewCategorySet()
    category_set.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Rooms))
    # create a new parameter binding
    new_parameter_binding = app.Create.NewInstanceBinding(category_set)
    # create a parameter definition
    new_parameter_definition = app.Create.NewP
    # create a new parameter
    doc.ParameterBindings.Insert(parametertoadd,new_parameter_binding)