# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Open the current project's home page on Autodesk Construction Cloud (ACC) in the default web browser.

The project must be hosted on ACC / BIM 360 for this to work; local files will be reported with a friendly message.
"""
import webbrowser

from pyrevit import revit, DB, forms, script

__title__ = "Go To ACC"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc

try:
    hub_id = DB.Document.GetHubId(doc)
    proj_id = DB.Document.GetProjectId(doc)
except Exception:
    forms.alert("This tool only works for projects hosted on Autodesk Construction Cloud (ACC) or BIM 360.",
                title="Not a Cloud Project",
                warn_icon=True,
                exitscript=True)

if not hub_id or not proj_id:
    forms.alert("Could not resolve the hub or project id for the current document.",
                title="Project IDs Missing",
                warn_icon=True,
                exitscript=True)

# Strip the two-character schema prefix (e.g. "b.") that GetHubId/GetProjectId return.
hub_str = hub_id[2:]
proj_str = proj_id[2:]
acc_url = "https://acc.autodesk.com/insight/accounts/{}/projects/{}/home".format(hub_str, proj_str)

webbrowser.open_new_tab(acc_url)
