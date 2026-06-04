# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Open the current project's folder on the local Autodesk Desktop Connector (ADC) mirror in File Explorer.

Useful for jumping straight to the project's sibling files (PDFs, references, exports)
without leaving Revit. The project must be hosted on ACC / BIM 360 and accessible
through ADC for this to work.
"""
import os

from pyrevit import revit, forms, script
from pyrevit.interop import adc

__title__ = "Find in ADC"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc
doc_save_path = doc.PathName


def _get_organization_name(drv_info, path):
    """Resolve the organization-name segment of an ADC drive path by scanning the local mirror."""
    drive_schema = adc.ADC_DRIVE_SCHEMA.format(drive_name=drv_info.Name)
    parts = path.replace(drive_schema, "").split('/')
    file_name = parts[1]
    drv_local_path = os.path.normpath(drv_info.WorkspaceLocation)
    for root, _dirs, files in os.walk(drv_local_path):
        for f in files:
            if f == file_name:
                file_path = os.path.join(root, f)
                return file_path.replace(drv_local_path, "").split(os.sep)[1]
    return None


def get_local_model_path(path):
    """Return the local ADC mirror path for the given cloud document path, or None."""
    adc_obj = adc._get_adc()
    drv_info = adc._get_drive_from_path(adc_obj, path)
    if not drv_info:
        return None
    org_name = _get_organization_name(drv_info, path)
    if not org_name:
        return None
    drv_schema = adc.ADC_DRIVE_SCHEMA.format(drive_name=drv_info.Name)
    rel_path = path.replace(drv_schema, "")
    return os.path.normpath(os.path.join(drv_info.WorkspaceLocation, org_name, rel_path))


if not doc_save_path:
    forms.alert("Save the project first — unsaved documents have no path to resolve.",
                title="No File Path",
                warn_icon=True,
                exitscript=True)

try:
    adc._get_adc()
except Exception:
    forms.alert("Autodesk Desktop Connector is not available.\n\n"
                "Make sure ADC is installed, running, and signed in, then try again.",
                title="ADC Not Found",
                warn_icon=True,
                exitscript=True)

local_model_path = get_local_model_path(doc_save_path)
if not local_model_path:
    forms.alert("Could not resolve a local ADC mirror path for this document.\n\n"
                "Cloud path: {}".format(doc_save_path),
                title="Path Not Resolved",
                warn_icon=True,
                exitscript=True)

project_files_dir = os.path.join(os.path.dirname(local_model_path), "Project Files")
target_dir = project_files_dir if os.path.isdir(project_files_dir) else os.path.dirname(local_model_path)

if not os.path.isdir(target_dir):
    forms.alert("The local folder for this project does not exist on disk.\n\n"
                "Expected: {}".format(target_dir),
                title="Path Not Found",
                warn_icon=True,
                exitscript=True)

os.startfile(target_dir)
