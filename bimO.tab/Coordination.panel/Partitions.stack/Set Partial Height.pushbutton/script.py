import pyrevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import output

from System.Collections.Generic import List

#import .NET libraries
import clr
clr.AddReference('RevitAPI')
clr.AddReference('ProtoGeometry')
clr.AddReference('RevitNodes')
clr.AddReference('RevitServices')  # Add this line
from Autodesk.Revit.DB import *
import Autodesk.DesignScript.Geometry as DS
from Autodesk.DesignScript.Geometry import *
import RevitServices




doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# Get the list of all levels in the model using pyrevit's selectlevel form
levels = forms.select_levels(title='Select Levels', button_name='Select Levels', multiple=True)
if not levels:
    activeview = True
else: activeview = False

# Get all the ceilings in the model
ceilings = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
# filter the ceilings based on the selected levels
selectedceilings = []
for ceiling in ceilings:
    if ceiling.LevelId in [level.Id for level in levels]:
        selectedceilings.append(ceiling)

# Use designscript to get the very bottom surfaces of the ceilings
bottomsurfaces = []
for ceiling in selectedceilings:
    # get the geometry of the ceiling
    surface1 = DB.Element.GetGeometryObjectFromReference(ceiling.GetBottomSurfaceReference())
    #unwrapping the geometry
    dsgeometry = surface1.ToProtoType()
    print(dsgeometry)



# Get the list of all the wall types in the model
walltypes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
# Filter the wall types using selectfromlist form
walltypenames = []
for walltype in walltypes:
    walltypename = walltype.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
    walltypenames.append(walltypename)
selectedwalltype = forms.SelectFromList.show(walltypenames, 
                                            button_name='Select Wall Types', 
                                            multiselect=True)

if not selectedwalltype:
    script.exit()

# Get the list of all the walls in the model
if activeview:
    wall_collector = DB.FilteredElementCollector(doc, uidoc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
else:
    allwalls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    wall_collector = []
    for wall in allwalls:
        if wall.LevelId in [level.Id for level in levels] and DB.Wall.CanHaveProfileSketch(wall):
            wall_collector.append(wall)

# Filter the walls based on the selected wall types
selectedwalls = []
for wall in wall_collector:
    for selectedtype in selectedwalltype:
        if wall.Name.Contains(selectedtype):
            selectedwalls.append(wall)

# Get the wall location curves using designscript library
wallcurves = []
cicles = []
for wall in selectedwalls:
    walllocation = wall.Location
    if isinstance(walllocation, LocationCurve):
        wallcurve = walllocation.Curve
        wallcurves.append(wallcurve)
        # get the midpoints of the wall curve
        wallpoints = []
        wallpoints.append(wallcurve.Evaluate(0.5, True))
        print(wallcurve.Evaluate(0.5, True))
        #draw 12" circle at the midpoints of the wall curve
        for point in wallpoints:
            centerpt = DS.Geometry.Point.ByCoordinates(point.X, point.Y, point.Z)
            circle = DS.Geometry.Circle.ByCenterPointRadius(centerpt, 1)
            cicles.append(circle)
