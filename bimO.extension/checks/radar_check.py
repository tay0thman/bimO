# -*- coding: utf-8 -*-
# region Imports
import math
from pyrevit import revit, DB, DOCS, HOST_APP
from pyrevit import script
from pyrevit.preflight import PreflightTestCase
# endregion
# region Constants
doc = DOCS.doc  # Current Document
output = script.get_output()
divider = "_" * 200
test_score = 0
INTERNAL_ORIGIN = (0, 0, 0)
EXTENT_DISTANCE = 52800  # Linear Feet
BAD_STRG = '### :thumbs_down_medium_skin_tone: ............'
GOOD_STRG = '### :OK_hand_medium_skin_tone: ............'
WARN_STRG = '### :warning: ............'
CRITERIA_STRG = '10 Mi (16KM) away from the Internal Origin.'
# endregion
# region Functions
def class_collectors(document=doc, class_type=None, toggle=False):
    """
    Collects all elements of a specified class type.
    Args:
        doc (Document): The current document.
        class_type (class): The class type to collect.
        toggle (bool): Whether to toggle the "OfClass" method on not
    Returns:
        elements (list): A list of elements of the specified class type.
    """
    if toggle:
        elements = (DB.FilteredElementCollector(document).
                WhereElementIsNotElementType().
                OfClass(class_type).
                ToElementIds())
    else:
        elements = (DB.FilteredElementCollector(document).
                WhereElementIsNotElementType.
                ToElementIds())
    return elements

def make_temp_view(document=doc, object=None):
    """
    Creates a temporary 3D view with the specified name.
    Args:
        doc (Document): The current document.
        object (Element): The element to isolate in the temporary view.
    Returns:
        view (View3D): The temporary 3D view.
    """
    view_3D_types = (DB.FilteredElementCollector(document)
                     .OfClass(DB.ViewFamilyType)
                     .WhereElementIsElementType()
                     .ToElements())
    three_d_view_type = ([v for v in view_3D_types 
                          if v.ViewFamily == DB.ViewFamily.ThreeDimensional][0])
    
    view = DB.View3D.CreateIsometric(document, three_d_view_type.Id)
    worksets = (DB.FilteredWorksetCollector(document).
                OfKind(DB.WorksetKind.UserWorkset).
                ToWorksets())
    for ws in worksets:
        view.SetWorksetVisibility(ws.Id, DB.WorksetVisibility.Visible)
    view.IsSectionBoxActive = True
    if object is not None:
             view.IsolateElementTemporary(object.Id)
    return view

def get_temp_view_bbox(document=doc):
    """
    Gets the bounding box of the 3D view.
    Args:
        doc (Document): The current document.
    Returns:
        bbox (BoundingBoxXYZ): The bounding box of the 3D view."""
    view = make_temp_view(document)
    bbox = view.GetSectionBox()
    return bbox

def hide_linked_elements(document=doc, 
                  view=None, 
                  hide_cads=True, 
                  hide_rvts=True):
    """
    Hides all Revit Links and CAD Links in the 3D view
    
    Args:
        doc (Document): The current document.
        view (View3D): The 3D view to hide the elements in.
        hide_cads (bool): Whether to hide CAD Links.
        hide_rvts (bool): Whether to hide Revit Links.
    Returns:
        None
    """
    revit_link_types = get_all_rvts(document)
    cads_link_types = get_all_cads(document)

    if revit_link_types and hide_rvts:
        view.HideElements(revit_link_types)
    if cads_link_types and hide_cads:
        (view.HideElements(cads_link_types))
        
def get_all_cads(document=doc):
    """
    Gets all CAD Links in the model.
    Args:
        doc (Document): The current document.
    Returns:
        cads (list): A list of CAD Links in the model.
        """
    cads = class_collectors(document, DB.ImportInstance, True)
    return cads

def get_all_rvts(document=doc):
    """
    Gets all Revit Links in the model.
    Args:
        doc (Document): The current document.
    Returns:
        rvts (list): A list of Revit Links in the model.
        """
    rvts = class_collectors(document, DB.RevitLinkInstance, True)
    return rvts

def get_far_elements(document=doc, cad=False, rvt=False, others=False):
    """
    Gets all elements that are more than 10 miles from the internal origin.
    Args:
        doc (Document): The current document.
        cad (bool): Whether to check CAD Links.
        rvt (bool): Whether to check Revit Links.
        others (bool): Whether to check other elements.
    Returns:
        bad_elements (list): A list of elements that are more than 10 miles
        from the internal origin.
        """
    bad_elements = []
    temp_view = make_temp_view(document)
    if cad:
        elementsids = (get_all_cads(document))
        temp_view.IsolateElementsTemporary(elementsids)
    elif rvt:
        elementsids = (get_all_rvts(document))
        temp_view.IsolateElementsTemporary(elementsids)
    elif others:
        hide_linked_elements(document,
                        temp_view,
                        hide_cads=True,
                        hide_rvts=True)
        elementsids = (DB.FilteredElementCollector(document, temp_view.Id).
                        WhereElementIsNotElementType().
                        ToElementIds())
    for elementid in elementsids:
        element = document.GetElement(elementid)
        if ((element.get_BoundingBox(temp_view)) and
             (hasattr(element, 'Name') and hasattr(element, 'Category'))):
            bbox = element.get_BoundingBox(temp_view)
            if (check_bounding_box(bbox, INTERNAL_ORIGIN, EXTENT_DISTANCE)
                    == 0):
                bad_elements.append(element)
    return bad_elements

def convert_values(value, document=doc):
    """
    Converts internal units to display units.
    Args:
        value (float): The value in internal system units to be converted.
        document (Document): The document object containing unit settings.
    Returns:
        str: The value converted to display units.
    """

    if HOST_APP.is_newer_than(2021):
        ui_units = (document.GetUnits().GetFormatOptions(DB.SpecTypeId.Length)
                    .GetUnitTypeId())
    else:
        ui_units = (document.GetUnits().GetFormatOptions(DB.UnitType.UT_Length)
                    .DisplayUnits)

    ui_values = DB.UnitUtils.ConvertFromInternalUnits(value, ui_units)
    ui_values = round(ui_values, 3)
    ui_values = str(ui_values).rstrip('0').rstrip('.')
    return ui_values

def convert_units(distance, document=doc):
    """
    Converts internal units to display units.
    Args:
        distance (float): The distance in internal system units to be converted.
        document (Document): The document object containing unit settings.
    Returns:
        str: The distance converted to display units.
    """    

    if HOST_APP.is_newer_than(2021):
        ui_units = DB.UnitFormatUtils.Format(units=document.GetUnits(),
                                            specTypeId=DB.SpecTypeId.Length,
                                            value=distance,
                                            forEditing=True)
    else:
        ui_units = DB.UnitFormatUtils.Format(units=document.GetUnits(),
                                             unitType=DB.UnitType.UT_Length, 
                                             value=distance, maxAccuracy=False, 
                                             forEditing=True)
    return ui_units

def calculate_distance(point1, point2):
    """
    Calculates the distance between two points.
    Args:
        point1 (tuple): The coordinates of the first point.
        point2 (tuple): The coordinates of the second point.
    Returns:
        distance (float): The distance between the two points."""
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    # Calculate the distance using the Euclidean distance formula
    distance =( #rounded to the nearest inch
        math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2))
    return distance

def calculate_horizontal_distance(point1, point2):
    """Calculates the horizontal distance between two points."""
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def calculate_delta_x(point1, point2):
    """Calculates the delta X between two points."""
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    delta_x = x2 - x1
    return delta_x

def calculate_delta_y(point1, point2):
    """Calculates the delta Y between two points."""
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    delta_y = y2 - y1
    return delta_y

def calculate_angle(point1, point2):
    """
    Calculates the angle between two points.
    Args:
        point1 (tuple): The coordinates of the first point.
        point2 (tuple): The coordinates of the second point.
    Returns:
        angle (float): The angle between the two points."""
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    # Calculate the angle using the arctangent function
    angle = round(math.degrees(math.atan2(y2 - y1, x2 - x1)), 2)
    return angle

def check_bounding_box(bbox, intorig, extentdistance):
    """
    Checks if the domain of the bounding box is more than 10
     miles from the internal origin.
     Args:
        bbox (BoundingBoxXYZ): The bounding box to check.
        intorig (tuple): The coordinates of the internal origin.
        extentdistance (float): The distance from the internal origin.
    Returns:
        Status (int): The status of the bounding box."""
    min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
    max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    if (calculate_distance(min, intorig) > extentdistance or 
        calculate_distance(max, intorig) > extentdistance):
        Status = 0
    else:
        Status = 1
    return Status

def get_project_base_and_survey_pts(document=doc):
    """
    Gets the coordinates of the project base and survey points.
    Args:
        doc (Document): The current document.
    Returns:
        base_point_coordinates (tuple): The coordinates of the project base point.
        survey_point_coordinates (tuple): The coordinates of the survey point.
    """
    base_point = DB.BasePoint.GetProjectBasePoint(document).Position
    base_point_coordinates = (
                                base_point.X,
                                base_point.Y,
                                base_point.Z)
    survey_point = DB.BasePoint.GetSurveyPoint(document).Position
    survey_point_coordinates = (
                                survey_point.X,
                                survey_point.Y,
                                survey_point.Z)
    return base_point_coordinates, survey_point_coordinates

def get_model_units_type(document=doc):
    """
    Gets the display unit system of the model.
    Args:
        doc (Document): The current document.
    Returns:
        unitsystem (str): The display unit system of the model.
    """
    unitsystem = document.DisplayUnitSystem
    return unitsystem

def get_design_options_elements(document=doc):
    """
    Gets the elements in each design option.
    Args:
        doc (Document): The current document.
    Returns:
        design_options (list): A list of design options in the model.
        design_option_elements (list): A list of elements in each design option.
        design_option_sets (list): A list of design option sets in the model.
    """
    design_option_elements = []
    design_option_sets = []
    design_options = (DB.FilteredElementCollector(document).
                        OfClass(DB.DesignOption).
                        ToElements())

    for do in design_options:
        option_set_param = DB.BuiltInParameter.OPTION_SET_ID
        option_set_id = do.get_Parameter(option_set_param).AsElementId()
        design_option_sets.append(option_set_id)
        design_option_filter = DB.ElementDesignOptionFilter(do.Id)
        x = (DB.FilteredElementCollector(document).
                WherePasses(design_option_filter).
                ToElements())
        design_option_elements.append(x)
    return design_options, design_option_elements, design_option_sets
# endregion
# region Main Output Functions
def check_model_coordinates(document=doc):
    """
    Checks and reports the coordinates of the project base and survey points.
    Args:
        doc (Document): The current document.
    Returns:
        None
    """
    unit_system = get_model_units_type(document=doc)
    # _______________________________________________________________HTML Styles
    output = script.get_output()
    output.add_style('cover {color:black; font-size:24pt; font-weight:bold;}')
    output.add_style('header {color:black; font-size:15pt;}')
    output.print_html(
    ('<cover>__________:satellite_antenna:__10-Mile Radar___________</cover>'))
    print(divider)
    print("")
    output.print_md('# Checking model placement and coordinates')
    print(divider)
    # _____________________________Check the distances of base and survey points
    baspt, survpt = get_project_base_and_survey_pts(document)
    basptdistance = abs(calculate_distance(baspt, INTERNAL_ORIGIN))
    surveydistance = abs(calculate_distance(survpt, INTERNAL_ORIGIN))

    if basptdistance > EXTENT_DISTANCE:
        output.print_md('{} Base Point is more than {}'.format(BAD_STRG, CRITERIA_STRG))
    if surveydistance > EXTENT_DISTANCE:
        output.print_md('{} Survey Point is more than {}'.format(BAD_STRG, CRITERIA_STRG))
    else:
        output.print_md('{} Survey Point is less than {}'.format(GOOD_STRG, CRITERIA_STRG))
    basptdistance = calculate_distance(baspt, INTERNAL_ORIGIN)
    # ____________________________________Calculate the angle between the points
    baseptangle = calculate_angle(baspt, INTERNAL_ORIGIN)
    surveyptangle = calculate_angle(survpt, INTERNAL_ORIGIN)
    truenorthangle = calculate_angle(baspt, survpt)
    # _______________________________Print the Project Coordinates and Distances
    tbdata = [['Internal Origin Coordinates', 
        str(INTERNAL_ORIGIN[0]),str(INTERNAL_ORIGIN[1]),str(INTERNAL_ORIGIN[2]),
        ' ', ' '],
        ['Project Base Point Coordinates to Internal Origin', 
        str(convert_values(baspt[0],doc)),
        str(convert_values(baspt[1],doc)),
        str(convert_values(baspt[2], doc)), 
        str(convert_units(basptdistance, document)), baseptangle],
        ['Survey Point Coordinates to Internal Origin', 
        str(convert_values(survpt[0], doc)),
        str(convert_values(survpt[1], doc)),
        str(convert_values(survpt[2], doc)),
        str(convert_units(surveydistance, document)), surveyptangle],
        ['Project Base Point to Survey Delta X', ' ', ' ', ' ',
        str(convert_units(calculate_delta_x(
            baspt, survpt), document))],
        ['Project Base Point to Survey Delta Y', ' ', ' ', ' ',
        str(convert_units(calculate_delta_y(
            baspt, survpt), document))],
        ['Planar Distance between Base Point and Survey Point',
        ' ', ' ', ' ', 
        str(convert_units(calculate_horizontal_distance(
            baspt, survpt), document)),
            truenorthangle],
        ['Total Distance between Base Point and Survey Point',
        ' ', ' ', ' ',
        str(convert_units(calculate_distance(
            baspt, survpt), document)),
            ' '],
        ['Project Elevation', 
        ' ', ' ', str(convert_values(baspt[2], doc)),
        str(convert_units((survpt[2] - baspt[2]), document))]]
    # Print Table
    output.print_table(table_data=tbdata, 
                    title='Project Coordinates and Distances',
                    columns=
                        ['Coordinates',
                        ' X  ',
                        ' Y  ',
                        ' Z  ',
                        ' Distance (' + str(unit_system) + ')  ',
                        ' ANGLE (°)  '],
                    formats=['', '' , '', '', '', ''])

def check_model_extents(document=doc):
    """
    Checks the extents of all elements in the model.
    Args:
        doc (Document): The current document.
    Returns:
        None
    """
        # _______________________________________Get the bounding box of the 3D view
    print("")
    output.print_md('# Checking the extents of the 3D view bounding box')
    bbox = get_temp_view_bbox(doc)
    min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
    max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    print("")
    print(divider)
    print("")
    if (calculate_distance(min, INTERNAL_ORIGIN) > EXTENT_DISTANCE or 
        calculate_distance(max, INTERNAL_ORIGIN) > EXTENT_DISTANCE):
        output.print_md('{} 3D View Bounding Box extends more than {}'.format(BAD_STRG, CRITERIA_STRG))
    else:
        output.print_md('{} 3D View Bounding Box is located less than {}'.format(GOOD_STRG, CRITERIA_STRG))
        test_score = 1

def check_design_options(document=doc):
    """
    Checks the extents of the design options in the model.
    Args:
        doc (Document): The current document.
    Returns:
        None
    """
    
        # _____________________________________________Get Objects in Design Options
    print("")
    print(divider)
    output.print_md('# Checking the extents of the design option objects')
    print(divider)
    design_option_objects = get_design_options_elements(document)
    violating_design_option_objects = []
    violating_options = []
    violating_option_sets = []
    option_set_param = DB.BuiltInParameter.OPTION_SET_ID
    
    for x in design_option_objects[1]:
        for y in x:
            dbbox = y.get_BoundingBox(None)
            if dbbox is None:
                continue
            else:
                dbmin = (dbbox.Min.X, dbbox.Min.Y, dbbox.Min.Z)
                dbmax = (dbbox.Max.X, dbbox.Max.Y, dbbox.Max.Z)
                if (calculate_distance(dbmin, INTERNAL_ORIGIN) > EXTENT_DISTANCE
                or 
                calculate_distance(dbmax, INTERNAL_ORIGIN) > EXTENT_DISTANCE):
                    violating_design_option_objects.append(y)
                    if y.DesignOption.Name not in violating_options:
                        violating_options.append(y.DesignOption)
                        violating_option_sets.append(
                                                y.DesignOption.
                                                get_Parameter(option_set_param).
                                                AsElementId())
    if len(violating_design_option_objects) > 0:
        output.print_md(BAD_STRG + 
        'Design Option Objects are located more than {}'.format(CRITERIA_STRG))
        if len(violating_design_option_objects) > 10:
            output.print_md('{} Showing the first 10 objects'.format(WARN_STRG))
            output.print_md('{} Manual investigation is required'.format(WARN_STRG))
        counter = 0
        limit = 10
        for x in violating_design_option_objects:
            if counter > limit:
                break
            else:
                    setid = violating_option_sets[counter]
                    print(output.linkify(x.Id) + 
                            "   " +
                            str(x.Name) +
                            " - Is part of " +
                            str(doc.GetElement(setid).Name) +
                            " - " +
                            str(x.DesignOption.Name)
                            )
                    counter += 1
        test_score = 0
    else:
        output.print_md('{} No object in any design option is located more than {}'.format(GOOD_STRG, CRITERIA_STRG))
        test_score = 1
    # __________________________________________________________Check Test Score
    if test_score >= 2:
        output.print_md('{} All Tests Passed.'.format(GOOD_STRG))
        script.exit()
    else:
        output.print_md( 
        '{} Distant objects detected, Proceeding with additional analysis'.format(BAD_STRG))

def check_linked_elements(document=doc):

    print(divider)
    output.print_md('# Checking the extents of the CAD and RVT links')
    print(divider)
    badcads = get_far_elements(doc, cad=True, rvt=False)
    badrvts = get_far_elements(doc, cad=False, rvt=True)
    counter = 0
    limit = 5
    if len(badcads) > 0 or len(badrvts) > 0:
        for x in badcads:
            print(output.linkify(x.Id)+"__" + 
                str(x.Name) + '  ' + str(x.Category.Name))
            if counter == limit:
                break
            counter += 1
        counter = 0
        for x in badrvts:
            print(output.linkify(x.Id)+"__" + 
                str(x.Name) + '  ' + str(x.Category.Name))
            if counter == limit:
                break
            counter += 1
    else:
        output.print_md('{} All CAD and RVT Links are located less than {}'.format(GOOD_STRG, CRITERIA_STRG))
        test_score = 2
        print(divider)

    hide_linked_elements(document, make_temp_view(document), True, True)
    cleanbbox = get_temp_view_bbox(doc)
    if check_bounding_box(cleanbbox, INTERNAL_ORIGIN, EXTENT_DISTANCE) == 0:
        output.print_md('{} Distant objects are still being detected!'.format(BAD_STRG))
        output.print_md('{} Further Analysis Required.'.format(WARN_STRG))
    else:
        output.print_md('{} All Objects are located less than {}'.format(GOOD_STRG, CRITERIA_STRG))
        script.exit()
    print(divider)
    output.print_md('# Checking everything, It is going to take a while.')
    output.print_md('# Please be patient.')

def check_all_elements(document=doc):
    """
    Checks the extents of all elements in the model.
    Args:
        doc (Document): The current document.
    Returns:
        None
        """
    print(divider)

    badelements = get_far_elements(document,False, False, True)                                          
    counter = 0
    limit = 10
    if len(badelements) > 0:
        if len(badelements) > limit:
            output.print_md('{} Showing the first 10 objects'.format(WARN_STRG))
            output.print_md('{} Manual investigation is required'.format(WARN_STRG))
        output.print_md('{} Elements below are located more than {}'.format(BAD_STRG, CRITERIA_STRG))
        for x in badelements:
            print(output.linkify(x.Id)+ '  ' + 
                    str(x.Name) + '  ' + str(x.Category.Name))
            if counter == limit:
                break
            counter += 1
    else:
        output.print_md('{} All Objects are located less than {}'.format(GOOD_STRG, CRITERIA_STRG))
        test_score += 1
    output.print_md('# All tests completed, Review the results above.')
# endregion
# region Preflight Test Case
class ModelChecker(PreflightTestCase):
    """
    Checks the extents of all elements in the model.
    This Model Checker swiftly verifies the extents of the Revit model. 
    Placing model extents more than 10 Mi (16KM) from the project's 
    internal origin can lead to issues with accuracy, tolerance, 
    performance, and viewport display. This check ensures that the 
    model remains within a 10-mile radius of the internal origin.

    The test case examines the following, reporting extents 
    concerning the project's internal origin. The script prioritizes 
    based on the assumption that most model extent issues are
    related to the following:

        - The distance between project basepoint and internal origin
        - The distance between survey point and  internal origin
        - The bounding box of the 3D view
        - The bounding box of the design option objects
        - The bounding box of the CAD and RVT links
        - The bounding box of all elements in the model
    """
    name = "10 Mile Radar"
    author = "Tay Othman"

    def setUp(self, doc, output):
        pass

    def startTest(self, doc, output):
        with revit.DryTransaction("Checking Model Extents"):
            check_model_coordinates(doc)
            check_model_extents(doc)
            check_design_options(doc)
            check_linked_elements(doc)
            check_all_elements(doc)

    def tearDown(self, doc, output):
        pass

    def doCleanups(self, doc, output):
        pass
# endregion