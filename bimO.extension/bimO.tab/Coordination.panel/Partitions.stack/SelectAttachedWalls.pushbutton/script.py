#this script will select all the walls that are current attached at top using the value of the parameter WALL_TOP_IS_ATTACHED
# this script uses pyrevit

import pyrevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import output
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Get the list of all levels in the model using pyrevit's selectlevel form
levels = forms.select_levels(title='Select Levels', button_name='Select Levels', multiple=True)
if not levels:
    activeview = True
else: activeview = False


#use pyrevit form checkboxes to get a list of wall types to filter
walltypes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
walltypenames = []
for walltype in walltypes:
    #get the name of the wall type
    walltypename = walltype.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    walltypenames.append(walltypename)

# use the SelectFromList form to get the wall types as names and output the selected wall types, if none selected, the script will exit
typefiltername = forms.SelectFromList.show(walltypenames, button_name='Select Wall Types', multiselect=True)
if not typefiltername:
    # print html message to the output
    # define h3 style with color red
    output = script.get_output()
    output.add_style('body { font-family: Calibri; font-size: 18px;  color: #FF0000;}')
    output.print_html('<div class=body>!!  No wall types selected, script will exit  !!</div>')
    raise SystemExit


# get all the walls in the model that belong to the category OST_Walls and has a type name that contains the string "Braced"
if activeview:
    wall_collector = DB.FilteredElementCollector(doc, uidoc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
else:
    allwalls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    wall_collector = []
    for wall in allwalls:
        if wall.LevelId in [level.Id for level in levels] and DB.Wall.CanHaveProfileSketch(wall):
            wall_collector.append(wall)
#filter the walls that have the parameter WALL_TOP_IS_ATTACHED set to true
attached_braced_walls = []
for wall in wall_collector:
    for filtername in typefiltername:
        if wall.Name.Contains(filtername):
             if wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_IS_ATTACHED).AsInteger() == 1:
                attached_braced_walls.append(wall)

            
#exclude infill walls from the list
attached_braced_walls = [wall for wall in attached_braced_walls if wall.HasPhases]
#select the walls in the model
uidoc.Selection.SetElementIds(List[DB.ElementId]([wall.Id for wall in attached_braced_walls]))