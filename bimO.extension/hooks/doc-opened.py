
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
import datetime

if datetime.datetime.today().weekday() == 4 and datetime.datetime.now().hour >= 14:
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
        print('Done Deleting')
        print('Deleted Sections:')
        print(len(sectionstodelete))
        print('Deleted Drafting Views:')
        print(len(draftingviewstodelete))
        print('Deleted Elevations:')
        print(len(elevationstodelete))
        print('Deleted 3D Views:')
        print(len(threedviewstodelete))
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

     
