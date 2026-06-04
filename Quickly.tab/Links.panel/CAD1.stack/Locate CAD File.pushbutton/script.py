# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Open the folder containing the source DWG/DXF file for the selected CAD link."""

import os

from pyrevit import revit, DB, forms, script

__title__ = "Locate CAD\nFile"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

selection = revit.get_selection()
if not selection:
    forms.alert("Select a CAD link in the view first, then run this tool.",
                exitscript=True)

selected_element = selection[0]
if not isinstance(selected_element, DB.ImportInstance):
    forms.alert("Selected element is not a CAD link or import.\n"
                "Pick a DWG/DXF link in the view.",
                exitscript=True)

cad_link_type = doc.GetElement(selected_element.GetTypeId())
if cad_link_type is None or not cad_link_type.IsExternalFileReference():
    forms.alert("Selected CAD is embedded (imported), not linked.\n"
                "Only linked CAD files have a resolvable source path.",
                exitscript=True)

external_ref = cad_link_type.GetExternalFileReference()
model_path = external_ref.GetAbsolutePath()
cad_file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(model_path)

if not cad_file_path:
    forms.alert("Could not resolve a file path for this CAD link.",
                exitscript=True)

cad_folder = os.path.dirname(cad_file_path)
if not os.path.isdir(cad_folder):
    forms.alert("File path is recorded but the folder no longer exists:\n{}"
                .format(cad_folder),
                exitscript=True)

os.startfile(cad_folder)
