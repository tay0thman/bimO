"""Select multiple sheets from a list"""
#pylint: disable=import-error,invalid-name

from Autodesk.Revit.DB import *
from pyrevit import forms, revit, DB
import csv
__title__ = 'Detail Sorting'
__author__  = 'Tay Othman, AIA'

# Set the active Revit application and document
doc = revit.doc

# Define Functions
# Define a function to clean the string
def clean_string(text):
    if "-" in text[:5]:
        fragment1 = text[:8]
        if "-" in fragment1 and not any(x in fragment1 for x in ["HOUR", "HR", "RATED"]):
            frag1new = fragment1.split("-")[-1]
        else:
            frag1new = fragment1
        fragment2 = text[8:]
        new_text = frag1new + fragment2
    else:
        new_text = text
    return new_text

# Define a function to Combine View number and View Name

def combine_view_number_and_name(view_number, view_name, sheet_number):
    view_number = str(view_number)  # remove leading zeros
    return sheet_number + "-" + view_number + " - " + view_name

    
selection = revit.get_selection()
sel_sheets = forms.select_sheets(title='Select Sheets')
# sel_sheets = [sheet for sheet in forms.select_sheets(title='Select Sheets') if isinstance(sheet, ViewSheet)]

if sel_sheets:
    selection.set_to(sel_sheets)
else: sys.exit()

# Create a dictionary to store viewports on each sheet
if sel_sheets:
    viewport_dict = {}
    for sheet in sel_sheets:
        viewport_dict[sheet] = []

    # Add viewports to the dictionary
    for sheet in sel_sheets:
        for viewport_id in sheet.GetAllViewports():
            viewport = doc.GetElement(viewport_id)
            #Extract Viewport Name
            vnam = viewport.get_Parameter(BuiltInParameter.VIEWPORT_VIEW_NAME).AsString()
            #Extract View Id
            view_id = viewport.ViewId
            rawshnum = sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
            shnum = rawshnum.replace(".", "")
            #Extract Detail Number
            vnum = viewport.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).AsString()
            #Extract Viewport Name remove any Risiduals from the previous name
            newvnam = clean_string(vnam)
            # print (shnum + "-" + vnum + " - " + vnam)
            viewport_dict[sheet].append((view_id, shnum, vnum, vnam , newvnam))



# Define the file path and name for the CSV file
#csv_file = r'C:\Users\TOthman\Desktop\test\pre_viewport_data.csv'

# Open the CSV file for writing
#with open(csv_file, 'wb') as file:
#    writer = csv.writer(file)

    # Write the header row
#    writer.writerow(['ID', 'Sheet Number', 'Detail Number', 'VP Old Name', 'VP New Name'])

    # Write the data rows
#    for sheet, viewports in viewport_dict.items():
#        for viewport in viewports:
            # Write the data row
#            writer.writerow([viewport[0], viewport[1], viewport[2], viewport[3], viewport[4]])
            # evaluate and print the difference
#           if viewport[3] != viewport[4]:
#                print(viewport[3] + "       >>>>>>>>          " + viewport[4])

# Create a list of old and new viewport names
oldVPnames = []
newVPnames = []
for sheet, viewports in viewport_dict.items():
    for viewport in viewports:
        oldVPname = viewport[3]
        oldVPnames.append(oldVPname)
        newVPname = combine_view_number_and_name(viewport[2], viewport[4], viewport[1])
        newVPnames.append(newVPname)

# Create a list of changes
changes = [old + "          >>>>>>>>            " + new for old, new in zip(oldVPnames, newVPnames)]

# Display a confirmation dialog box
proceed = forms.alert("List of changes:\n\n{}\n\nProceed?".format('\n'.join(changes)), ok=True, cancel=False, exitscript=False)
if proceed:
    # Push Changes to the Revit Sheets
        for sheet, viewports in viewport_dict.items():
            for viewport in viewports:
                newVPname = combine_view_number_and_name(viewport[2], viewport[4], viewport[1])
                # get the viewport element
                view_id = viewport[0]
                view = doc.GetElement(view_id)
                # Set the VIEW_NAME and VIEW_DESCRIPTION properties
                with Transaction(doc, 'Set View Properties') as tx:
                    tx.Start()
                    view.get_Parameter(BuiltInParameter.VIEW_NAME).Set(newVPname)
                    view.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(viewport[4])
                    tx.Commit()


            forms.show_balloon("Done Renaming All The Viewports of This Sheet", "Done Renaming All The Viewports of This Sheet", "information")
else:
    forms.alert("Operation Cancelled", title="Viewport Renaming")