# -*- coding: utf-8 -*-
# pylint: disable=import-error
# pylint: disable=invalid-name, no-member, too-many-locals, unused-import
from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List

from rpw.ui.forms import FlexForm, Label, Separator, Button, ComboBox, CheckBox

doc = revit.doc
uidoc = revit.uidoc

def create_detail_lines_from_geometry(
                                            geometry_elements,
                                            filled_region_type,
                                            line_style):
    """Create detail lines from the geometry of an import instance.
    args:
        geometry_elements: The geometry elements of the import instance.
    return: The created detail lines."""
    ids = []
    x = None

    for g in geometry_elements:
            try:
                styleid = g.GraphicsStyleId
                stylecat = doc.GetElement(styleid).GraphicsStyleCategory
                # get the category name
                catname = stylecat.Name
                #get category lineweight
                lineweight = stylecat.LineWeight
                print("Category Name:", lineweight)
            except Exception as e:
                print("{} {}".format("Skipped>>", e))

            if "PolyLine" in str(g):
                polyline = DB.PolyLine.Clone(g)
                # get coordinates of the polyline
                points = polyline.GetCoordinates()
                # create detail lines for each segment
                for i in range(len(points) - 1):
                    try:
                        line = DB.Line.CreateBound(points[i], points[i + 1])
                        poly = doc.Create.NewDetailCurve(doc.ActiveView, line)
                        # set the line style of the detail line
                        poly.LineStyle = line_style
                        ids.append(poly.Id)
                        pass  # create detail line
                    except Exception as e:
                        print("{} {}".format("Skipped>>", e))
                        pass
            elif "Arc" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Arc.Clone(g))
                # set the line style of the detail line
                x.LineStyle = line_style
                
            elif "Ellipse" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Ellipse.Clone(g))
                x.LineStyle = line_style
            elif "Line" in str(g) and "PolyLine" not in str(g):
                style_id = g.GraphicsStyleId
                style_cat = doc.GetElement(style_id).GraphicsStyleCategory
                if "DIM" in str(style_cat.Name):
                    pass
                else:
                    x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Line.Clone(g))
                    x.LineStyle = line_style
            elif "Curve" in str(g):
                x = doc.Create.NewDetailCurve(doc.ActiveView, DB.Curve.Clone(g))
                x.LineStyle = line_style
            elif "Solid" in str(g):
                create_filled_region(g, filled_region_type)
            else:
                print("Unknown geometry type:", str(g))
            if x:
                ids.append(x.Id)
    return ids

def create_filled_region(solid, filled_region_type):
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
    lines_category = \
        doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    subcategories = lines_category.SubCategories
    subcats_dict = {}
    for subcategory in subcategories:
        subcats_dict[
            subcategory.GetGraphicsStyle(DB.GraphicsStyleType.Projection)]\
         = subcategory.Name
    return {k: v for k, v in sorted(subcats_dict.items(), key=lambda x: x[1])}

def show_rpw_ui():
    """Show the rpw UI."""
    form = FlexForm("Select Options", [
        Label("Select a filled region type:"),
        ComboBox("filled_region_type", 
                    {str(t.LookupParameter("Type Name").AsString()): t for t in
                    query_filled_region_types()}),
        Separator(),
        Label("Select a line style:"),
        ComboBox("line_style", 
                                    {str(k.Name): k for k in 
                                    query_line_styles().keys()}),
        Separator(),
        Label("Halftone source CAD:"),
        CheckBox("halftone_source_cad", "Halftone Source CAD"),
        Button("OK"),
        Button("Cancel")
    ])
    form.show()
    if not form:
        forms.alert("User cancelled the operation.", exitscript=True)
    if "filled_region_type" not in form.values or "line_style" not in form.values:
        forms.alert("Operation Cancelled", exitscript=True)
    filled_region_type = form.values["filled_region_type"]
    line_style = form.values["line_style"]
    halftone_source_cad = form.values["halftone_source_cad"]
    return filled_region_type, line_style, halftone_source_cad

if __name__ == "__main__":
    filled_region = query_filled_region_types()
    line_style = query_line_styles()
    selected_types = show_rpw_ui()
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
    x = create_detail_lines_from_geometry(
                                            geometry_elements, 
                                            selected_types[0], 
                                            selected_types[1])
    if selected_types[2]:
        # set the detail lines to halftone
        override_settings = DB.OverrideGraphicSettings()
        override_settings.SetHalftone(True)
        doc.ActiveView.SetElementOverrides(import_instance.Id, override_settings)
    t.Commit()
    if x:
        # convert the list of element ids to Icollection
        dotnet_list = List[DB.ElementId](x)
        # assign to ICollection
        icoll = dotnet_list  # List[DB.ElementId] already implements ICollection
        uidoc.Selection.SetElementIds(icoll)
