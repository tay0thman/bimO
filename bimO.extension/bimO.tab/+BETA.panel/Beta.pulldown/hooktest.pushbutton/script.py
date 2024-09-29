
# from pyrevit import HOST_APP, EXEC_PARAMS
# args = EXEC_PARAMS.event_args

import pyrevit
from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
output = script.get_output()

doc = revit.doc

#Get all views in the project
views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()

viewnames = []
sectionstodelete = []
elevationstodelete = []
draftingviewstodelete = []
threedviewstodelete = []
paramname = "GetPlacementOnSheetStatus"
paramtarget = "CompletelyPlaced"
# test of view names start with "Section" or "Drafting"
for v in views:
    if v.Name.startswith("Section") and str(DB.View.GetPlacementOnSheetStatus(v)) != paramtarget:
        sectionstodelete.append(v)
    if v.Name.startswith("Drafting") and str(DB.View.GetPlacementOnSheetStatus(v)) != paramtarget:
        draftingviewstodelete.append(v)
    #test of elevation views start with "Number-Letter" like 1-c
    if v.Name[0].isdigit() and v.Name[1] == "-" and v.Name[2].isalpha() and str(DB.View.GetPlacementOnSheetStatus(v)) != paramtarget:
        elevationstodelete.append(v)
    # test if 3d views start with "3D-"
    if v.Name.startswith("3D View ") and str(DB.View.GetPlacementOnSheetStatus(v)) != paramtarget and v.Name != "3D View: Default 3D View":
        threedviewstodelete.append(v)
# define output styles
output.add_style('header {background-color: #ff0000; color: #ffffff; font-weight: bold; font-size: 24pt;}')
output.add_style('overriden {background-color: #ff0000; color: #ffffff; font-weight: bold;}')
output.add_style('truevalue {background-color: #ff0000; color: #ffffff; font-weight: bold;}')

for v in threedviewstodelete:
    output.print_html('<truevalue>{}</truevalue>'.format(v.Name))
# if today is friday after 2 pm delete, elsoe show warning
import datetime

if datetime.datetime.today().weekday() == 4 and datetime.datetime.now().hour >= 14:

    with DB.Transaction(doc, "Delete Views") as t:
        t.Start()
        for v in sectionstodelete:
            doc.Delete(v.Id)
        for v in draftingviewstodelete:
            doc.Delete(v.Id)
        for v in elevationstodelete:
            doc.Delete(v.Id)
        for v in threedviewstodelete:
            doc.Delete(v.Id)
        t.Commit()
        output.print_html('<h1 style="color:green; font-size: 28pt;">Done Deleting</h1>')
        output.print_html('<h2 style="color:green;">Deleted Sections:</h2>')
        output.print_html('<truevalue>{}</truevalue>'.format(len(sectionstodelete)))
        output.print_html('<h2 style="color:green;">Deleted Drafting Views:</h2>')
        output.print_html('<truevalue>{}</truevalue>'.format(len(draftingviewstodelete)))
        output.print_html('<h2 style="color:green;">Deleted Elevations:</h2>')
        output.print_html('<truevalue>{}</truevalue>'.format(len(elevationstodelete)))
        output.print_html('<h2 style="color:green;">Deleted 3D Views:</h2>')
        output.print_html('<truevalue>{}</truevalue>'.format(len(threedviewstodelete)))

else:
# Display Warning that views will be deleted this friday AT 2 PM    
    output.print_html('<h1 style="color:red;">WARNING! Views will be deleted this Friday at 2 PM</h1>')
    output.print_html('**Sections:**')
    for v in sectionstodelete:
        output.print_html('<truevalue>{}</truevalue>{}'.format(v.Name, output.linkify(v.Id)))
    output.print_html('**Drafting Views:**')
    for v in draftingviewstodelete:
        output.print_html('<truevalue>{}</truevalue>{}'.format(v.Name, output.linkify(v.Id)))
    output.print_html('**Elevations:**')
    for v in elevationstodelete:
        output.print_html('<truevalue>{}</truevalue>{}'.format(v.Name, output.linkify(v.Id)))
    output.print_html('**3D Views:**')
    for v in threedviewstodelete:
        output.print_html('<truevalue>{}</truevalue>{}'.format(v.Name, output.linkify(v.Id)))

     
