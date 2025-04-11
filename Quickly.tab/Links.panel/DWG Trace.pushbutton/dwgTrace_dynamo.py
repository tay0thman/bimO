# -*- coding: utf-8 -*-
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import UIApplication
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from System.Collections.Generic import List, ICollection

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument


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

def apply_graphics_style_to_lines(graphics_style, lines):
    """Apply a graphics style to the created detail lines.
    args:
        graphics_style: The graphics style to apply.
        lines: The created detail lines."""
    if graphics_style and lines:
        # Apply the graphics style to the detail lines
        for line in lines:
            line.LineStyle = graphics_style


def create_filled_region(solid):
    """Create a filled region from the geometry of an import instance.
    args:
        geometry: The geometry of the import instance.
    return: The created filled region."""
    # get the outline of the face
    curveloop = []
    face_array = solid.Faces
    for i in range(face_array.Size):
        face = face_array.get_Item(i)
        loops = face.GetEdgesAsCurveLoops()
        for loop in loops:
            curveloop.append(loop)
    # Create a filled region type if it doesn't exist
    filled_region_type = UnwrapElement(IN[2])
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

import_instance = UnwrapElement(IN[0])
line_graphics_style = UnwrapElement(IN[1])
halftone = IN[3]
if halftone:
        # construct halftone override graphic settings
        halftone = DB.OverrideGraphicSettings()
        halftone.SetHalftone(True)

geometry = import_instance.get_Geometry(Options())
geometry_elements = []
for geom in geometry:
    for g in geom.GetInstanceGeometry():
        geometry_elements.append(g)
t = Transaction(doc, "Trace Import Instance Geometry")
t.Start()
x = create_detail_lines_from_geometry(geometry_elements) #type: List[ElementId]
if x:
    # get the elements of the lines created
    x_elements = []
    for i in x:
        x_elements.append(doc.GetElement(i))
    apply_graphics_style_to_lines(line_graphics_style, x_elements)

if halftone:
        doc.ActiveView.SetElementOverrides(import_instance.Id, halftone)
t.Commit()
if x:
    OUT = x_elements