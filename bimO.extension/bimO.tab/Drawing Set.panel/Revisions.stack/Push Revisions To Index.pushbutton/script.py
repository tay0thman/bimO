"""Update Index with Revised Sheets"""
#updated by Tay Othman 2023-11-25

from pyrevit import revit, DB
from pyrevit import forms
import os
import sys

author = 'Tay Othman, AIA'

# Filter Function
param_filter_func = lambda p: '/' in p.name 

revisionsID = None
# Collect Revions in the Project
try: revisionsID = forms.select_revisions(button_name='Select Revised Sheets',
                                   multiple=False)
except: # if the user cancels the selection
    sys.exit()




# Query all sheets in the project that contains RevisionID or a clouded revision

sheets = DB.FilteredElementCollector(revit.doc)\
            .OfCategory(DB.BuiltInCategory.OST_Sheets)\
            .WhereElementIsNotElementType()\
            .ToElements()

# Filter sheets that contains the selected revision

sheetsToModify = []
if revisionsID == None:
    sys.exit()
else:
    print(revisionsID.Name)
for sheet in sheets:
    sheetrevs = sheet.GetAllRevisionIds()
    if sheetrevs.Contains(revisionsID.Id):
        sheetsToModify.append(sheet)

# Parameter Work
sh_Params = []
sheetTextParams = []

# Define Filtering Pattern to be '/' to get all the parameters
TargetParam = forms.select_parameters(sheetsToModify[0], title='Select Parameter to Update', filterfunc=param_filter_func,  button_name='Select Parameter', exclude_readonly=True)

# Start Revit Transaction and Loop through SheetsToModify and Update the Value of TargetParam to be 'X'
with revit.Transaction('Add Revised Sheets to Index'):
    for sheet in sheetsToModify:
        sheet.LookupParameter(TargetParam[0].name).Set('X')

# Report the number of sheets that has been updated
print('Number of Sheets Updated: {}'.format(len(sheetsToModify)))
print('_______________________________________List of Sheets Updated:')
for sheet in sheetsToModify:
            print("Sheet: " + sheet.SheetNumber + " - " + sheet.Name)