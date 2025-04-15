# -*- coding: utf-8 -*-
from pyrevit import revit, DB, forms, script, HOST_APP, UI
from System.Collections.Generic import List, ICollection

doc = revit.doc
uidoc = revit.uidoc

def create_detail_lines_from_geometry(geometry_elements):
    """Create detail lines from the geometry of an import instance.
    args:
        geometry_elements: The geometry elements of the import instance.
    return: The created detail lines."""
    ids = []
    x = None
    for g in geometry_elements:
            if "PolyLine" in str(g):
                polyline = DB.PolyLine.Clone(g)
                # get coordinates of the polyline
                points = polyline.GetCoordinates()
                # create detail lines for each segment
                for i in range(len(points) - 1):
                    try:
                        line = DB.Line.CreateBound(points[i], points[i + 1])
                        poly = doc.Create.NewDetailCurve(doc.ActiveView, line)
                        ids.append(poly.Id)
                        pass  # create detail line
                    except Exception as e:
                        print("{} {}".format("Skipped>>", e))
                        pass
            elif "Arc" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Arc.Clone(g))
            elif "Ellipse" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Ellipse.Clone(g))
            elif "Line" in str(g) and "PolyLine" not in str(g):
                style_id = g.GraphicsStyleId
                style_cat = doc.GetElement(style_id).GraphicsStyleCategory
                if "DIM" in str(style_cat.Name):
                    pass
                else:
                    x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Line.Clone(g))
            elif "Curve" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Curve.Clone(g))
            elif "Solid" in str(g):
                create_filled_region(g)
            else:
                print("Unknown geometry type:", str(g))
            if x:
                ids.append(x.Id)
    return ids

def create_filled_region(solid):
    """Create a filled region from the geometry of an import instance.
    args:
        geometry: The geometry of the import instance.
    return: The created filled region."""
    # get the outline of the face
    curveloop = []
    face_array = solid.Faces
    for i in range(face_array.Size):
        face = face_array.Item[i]
        loops = face.GetEdgesAsCurveLoops()
        for loop in loops:
            curveloop.append(loop)
    # Create a filled region type if it doesn't exist
    filled_region_type = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).FirstElement()
    if not filled_region_type:
        forms.alert("No Filled Region Type found in the document.", exitscript=True)
    try:
        filled_region = DB.FilledRegion.Create(doc, filled_region_type.Id, doc.ActiveView.Id, curveloop)
    except Exception as e:
            print("{} {}".format("Skipped>>", e))
            return
    return filled_region

def get_import_instance_geometry(import_instance):
    """Get the geometry of an import instance.
    args:
        import_instance: The import instance to get the geometry from.
    return: The geometry of the import instance."""
    options = DB.Options()
    geometry = import_instance.get_Geometry(options)
    return geometry

def get_import_instance():
    """Get the import instance from the active view.
    return: The import instance."""
    collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id)
    collector.OfClass(DB.ImportInstance)
    import_instances = collector.ToElements()
    return import_instances

def query_filled_region_types():
    """Query the filled region type from the user.
    return: The filled region type."""
    return DB.FilteredElementCollector(doc).\
                    OfClass(DB.FilledRegionType).\
                    WhereElementIsElementType().\
                    ToElements()

def query_line_styles():
    """Query the line styles from the revit document.
    return: Graphic Style Id."""
    return DB.FilteredElementCollector(doc).OfClass(DB.GraphicsStyle).ToElements()


print(query_line_styles())
print(query_filled_region_types())
script.exit

#prompt to select an Import Instance
selection = revit.pick_element(
    "Select an Import Instance to get its geometry")
if not selection:
    forms.alert("No import instance selected.", exitscript=True)
else:
    # Get the selected import instance geometry
    import_instance = selection
    if not isinstance(import_instance, DB.ImportInstance):
        forms.alert("Selected element is not an Import Instance.", exitscript=True)
    # Get the geometry of the import instance
    geometry = import_instance.get_Geometry(DB.Options())

geometry_elements = []
for geom in geometry:
    for g in geom.GetInstanceGeometry():
        geometry_elements.append(g)
t = DB.Transaction(doc, "Trace Import Instance Geometry")
t.Start()
x = create_detail_lines_from_geometry(geometry_elements)
t.Commit()
if x:
    # convert the list of element ids to Icollection
    dotnet_list = List[DB.ElementId](x)
    # assign to ICollection
    icoll = dotnet_list  # List[DB.ElementId] already implements ICollection
    uidoc.Selection.SetElementIds(icoll)
