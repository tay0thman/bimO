
from pyrevit import HOST_APP, EXEC_PARAMS
args = EXEC_PARAMS.event_args

import pyrevit
from pyrevit import revit, DB, UI
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
from pyrevit import output
output = script.get_output

doc = revit.__doc__

#Get all views in the project
views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
viewnames = []
sectionstodelete = []
elevationstodelete = []
draftingviewstodelete = []
threedviewstodelete = []



# test of view names start with "Section" or "Drafting"
for v in views:
    if v.Name.startswith("Section"):
        sectionstodelete.append(v)
    if v.Name.startswith("Drafting"):
        draftingviewstodelete.append(v)
    #test of elevation views start with "Number-Letter" like 1-c
    if v.Name[0].isdigit() and v.Name[1] == "-" and v.Name[2].isalpha():
        elevationstodelete.append(v)
    # test if 3d views start with "3D-"
    if v.Name.startswith("3D-"):
        threedviewstodelete.append(v)

# define output styles
output.add_style('header {background-color: #ff0000; color: #ffffff; font-weight: bold; font-size: 24pt;}')
output.add_style('overriden {background-color: #ff0000; color: #ffffff; font-weight: bold;}')
output.add_style('truevalue {background-color: #f38b0b; color: #ffffff; font-weight: bold;}')

# if today is friday after 2 pm delete, elsoe show warning
if coreutils.get_weekday() == 4 and coreutils.get_time().hour >= 14:
    #with DB.Transaction(doc, "Delete Views") as t:
     #   t.Start()
     #   for v in sectionstodelete:
     #       doc.Delete(v.Id)
     #   for v in draftingviewstodelete:
     #       doc.Delete(v.Id)
     #   for v in elevationstodelete:
     #       doc.Delete(v.Id)
     #   for v in 3dviewstodelete:
     #       doc.Delete(v.Id)
     #   t.Commit()
     print('Done Deleting' + (len(sectionstodelete) + len(elevationstodelete) + len(draftingviewstodelete) + len (threedviewstodelete)))
else:
# Display Warning that views will be deleted this friday AT 2 PM    
    output.print_md('**Warning:** Views will be deleted this friday at 2 PM', style='Header')
    output.print_md('**Sections:**', style='overriden')
    for v in sectionstodelete:
        output.print_md(v.Name, style='truevalue')
    output.print_md('**Drafting Views:**', style='overriden')
    for v in draftingviewstodelete:
        output.print_md(v.Name, style='truevalue')
    output.print_md('**Elevations:**', style='overriden')
    for v in elevationstodelete:
        output.print_md(v.Name, style='truevalue')
    output.print_md('**3D Views:**', style='overriden')
    for v in threedviewstodelete:
        output.print_md(v.Name, style='truevalue')

     
