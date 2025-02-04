pyRevit# -*- coding: utf-8 -*-

# ______________________________________________________________________Imports
# General Imports
# import sys
import math
# pyRevit
from pyrevit import revit, DB, DOCS, HOST_APP
from pyrevit import script
from pyrevit.preflight import PreflightTestCase

# ______________________________________________________________Global Variables
doc = DOCS.doc  #type:Document
INTERNAL_ORIGIN = (0, 0, 0)
EXTENT_DISTANCE = 52800  # Linear Feet
BAD_STRG = '### :thumbs_down_medium_skin_tone: ............'
GOOD_STRG = '### :OK_hand_medium_skin_tone: ............'
WARN_STRG = '### :warning: ............'

# ___________________________________________________3D to Bounding Box Analysis
class Get3DViewBoundingBox():
    def get_tempbbox(self, toggle_cads, toggle_rvts, toggle_ifcs, toggle_all):
        bad_cads = []
        bad_rvts = []
        bad_elements = []
        # Create a 3D view
        with revit.DryTransaction("Create 3D View"):
            view_3D_types = (DB.FilteredElementCollector(doc)
                            .OfClass(DB.ViewFamilyType)
                            .WhereElementIsElementType()
                            .ToElements())
            three_d_view_type = ([v for v in view_3D_types 
                if v.ViewFamily == DB.ViewFamily.ThreeDimensional][0])
            view = DB.View3D.CreateIsometric(doc, three_d_view_type.Id)
            worksets = (DB.FilteredWorksetCollector(doc).
                        OfKind(DB.WorksetKind.UserWorkset).
                        ToWorksets())
            for ws in worksets:
                view.SetWorksetVisibility(ws.Id, DB.WorksetVisibility.Visible)
            view.IsSectionBoxActive = True
            bb = view.GetSectionBox()
            if toggle_cads:
                cads = (DB.FilteredElementCollector(doc).
                        OfClass(DB.ImportInstance).
                        ToElements())
                if len(cads) == 0:
                    print("No CAD Links in the model")
                else:
                    for cad in cads:
                        cadbox = cad.get_BoundingBox(None)
                        cadmin = (cadbox.Min.X, cadbox.Min.Y, cadbox.Min.Z)
                        cadmax = (cadbox.Max.X, cadbox.Max.Y, cadbox.Max.Z)
                        if calculate_distance((
                            cadmin, INTERNAL_ORIGIN) > EXTENT_DISTANCE or
                            calculate_distance(cadmax, INTERNAL_ORIGIN) >
                             EXTENT_DISTANCE):
                            bad_cads.append(cad)
            if toggle_rvts:
                rvtlinks = (DB.FilteredElementCollector(doc).
                                OfClass(DB.RevitLinkInstance).
                                ToElements())
                if len(rvtlinks) == 0:
                    print("No RVT Links in the model")
                else:
                    for rvt in rvtlinks:
                        rvtbox = rvt.get_BoundingBox(view)
                        rvtmin = (rvtbox.Min.X, rvtbox.Min.Y, rvtbox.Min.Z)
                        rvtmax = (rvtbox.Max.X, rvtbox.Max.Y, rvtbox.Max.Z)
                        if (calculate_distance
                        (rvtmin, INTERNAL_ORIGIN) > EXTENT_DISTANCE or
                         calculate_distance
                        (rvtmax, INTERNAL_ORIGIN) > EXTENT_DISTANCE):
                            bad_rvts.append(rvt)
            if toggle_ifcs:
                pass
            revit_link_types = (DB.FilteredElementCollector(doc).
                                OfClass(DB.RevitLinkType).
                                ToElements())
            cads = (DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).
                    ToElements())
            if len(revit_link_types) > 0:
                (view.HideElements(DB.FilteredElementCollector(doc).
                    OfClass(DB.RevitLinkType).
                    ToElementIds()))
            if len(cads) > 0:
                (view.HideElements(DB.FilteredElementCollector(doc).
                OfClass(DB.ImportInstance).
                ToElementIds()))
            view.IsSectionBoxActive = False
            view.IsSectionBoxActive = True
            bbh = view.GetSectionBox()
            if toggle_all:
                elements = (DB.FilteredElementCollector(doc, view.Id).
                            WhereElementIsNotElementType().
                            ToElements())
                for element in elements:
                    if (element.get_BoundingBox(view) is not None and 
                    hasattr(element, 'Name') and hasattr(element, 'Category')):
                       bbox = element.get_BoundingBox(view)
                       if check_bounding_box(
                                bbox, INTERNAL_ORIGIN, EXTENT_DISTANCE) == 0:
                            bad_elements.append(element)
        return bb, bad_cads, bad_rvts, bbh, bad_elements

# ___________________________________________________________ Calculate Distance
def calculate_distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance


def convert_units(doc, distance):
    if HOST_APP.is_newer_than(2021):
        ui_units = DB.UnitFormatUtils.Format(units=doc.GetUnits(),
                                            specTypeId=DB.SpecTypeId.Length,
                                            value=distance,
                                            forEditing=False)
    else:
        ui_units = DB.UnitFormatUtils.Format(units=doc.GetUnits(),
                                             unitType=DB.UnitType.UT_Length, 
                                             value=distance, maxAccuracy=False, 
                                             forEditing=False)
    return ui_units


# ________________________________________________ Calculate Horizontal Distance
def calculate_horizontal_distance(point1, point2):
    # Unpack the tuples
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    # Calculate the distance using the Euclidean distance formula
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    delta_x = (x2 - x1)
    delta_y = (y2 - y1)
    return distance, delta_x, delta_y


# _____________________________________________________________ Get Bounding Box
def get_bounding_box(view):
    bb = view.CropBox
    min = bb.Min
    max = bb.Max
    return min, max


# _________________________________________________________ Analyze Bounding Box
def check_bounding_box(bbox, intorig, extentdistance):
    min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
    max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    if calculate_distance((min, intorig) > extentdistance or 
                            calculate_distance(max, intorig) > extentdistance):
        Status = 0
    else:
        Status = 1
    return Status


# ____________________________________________ Get ProjectBase and Survey Points
def get_project_base_and_survey_pts(document=doc):
    base_point = DB.BasePoint.GetProjectBasePoint(document).Position
    base_point_coordinates = (base_point.X, base_point.Y, base_point.Z)
    survey_point = DB.BasePoint.GetSurveyPoint(document).Position
    survey_point_coordinates = (survey_point.X, survey_point.Y, survey_point.Z)
    return base_point_coordinates, survey_point_coordinates, INTERNAL_ORIGIN


# _________________________________________________ Get Design Options & Objects
def get_design_options_elements(document=doc):
    design_option_elements = []
    design_options = (DB.FilteredElementCollector(document).
                        OfClass(DB.DesignOption).
                        ToElements())
    for do in design_options:
        design_option_filter = DB.ElementDesignOptionFilter(do.Id)
        x = (DB.FilteredElementCollector(document).
                WherePasses(design_option_filter).
                ToElements())
        design_option_elements.append(x)
    return design_options, design_option_elements


# ______________________________________________________________________________
# ________________________________________________________________ MAIN FUNCTION
# ______________________________________________________________________________
def check_model_extents(document=doc):
    # ______________________________________________HTML Styles
    output = script.get_output()
    output.add_style('cover {color:black; font-size:24pt; font-weight:bold;}')
    output.add_style('header {color:black; font-size:15pt;}')
    divider = "_"*100
    test_score = 0
    # _____________________________Check the distances of base and survey points
    output.print_html(
     ('<cover>__________:satellite_antenna:__10-Mile Radar___________</cover>'))
    print(divider)
    print("")
    output.print_md('# Checking model placement and coordinates')
    print(divider)
    baspt, survpt, INTERNAL_ORIGIN = get_project_base_and_survey_pts(document)
    basptdistance = abs(calculate_distance(baspt, INTERNAL_ORIGIN))
    surveydistance = abs(calculate_distance(survpt, INTERNAL_ORIGIN))
    if basptdistance > EXTENT_DISTANCE:
        output.print_md('BAD_STRG' + 
        'Base Point is more than 10 Mi (16KM) away from the Internal Origin.')
    if surveydistance > EXTENT_DISTANCE:
        output.print_md('BAD_STRG' + 
        'Survey Point is more than 10 Mi (16KM) away from the Internal Origin.')
    else:
        output.print_md('GOOD_STRG' + 
        'Survey Point is less than 10 Mi (16KM) away from the Internal Origin.')
    basptdistance = calculate_distance(baspt, INTERNAL_ORIGIN)
    tbdata = [['Internal Origin Coordinates', 
            str(INTERNAL_ORIGIN)],
            ['Project Base Point Coordinates', 
            str(baspt)],
            ['Survey Point Coordinates', 
            str(survpt)],
            ['Project Base Point Distance from Internal Origin', 
            str(convert_units(document, basptdistance))],
            ['Survey Point Distance from Internal Origin', 
            str(convert_units(document, surveydistance))],
            ['Project Base Point to Survey Delta X', 
            str(convert_units(document, 
                    calculate_horizontal_distance(baspt, survpt)[1]))],
            ['Project Base Point to Survey Delta Y', 
            str(convert_units(document, 
                    calculate_horizontal_distance(baspt, survpt)[2]))],
            ['Horizontal Distance between Project Base Point and Survey Point', 
            str(convert_units(document, 
                    calculate_horizontal_distance(baspt, survpt)[0]))],
            ['Project Elevation', 
            str(convert_units(document, (survpt[2] - baspt[2])))]]
    # Print Table
    output.print_table(table_data=tbdata, 
                       title='Project Coordinates and Distances',
                       columns=['Coordinates', 'Values'],
                       formats=['', ''])
    # _______________________________________Get the bounding box of the 3D view
    print("")
    output.print_md('# Checking the extents of the 3D view bounding box')
    bbox_instance = Get3DViewBoundingBox()
    bbox = bbox_instance.get_tempbbox(0,0,0,0)[0]
    min = (bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
    max = (bbox.Max.X, bbox.Max.Y, bbox.Max.Z)
    print("")
    print(divider)
    print("")
    if calculate_distance((min, INTERNAL_ORIGIN) > EXTENT_DISTANCE or 
        calculate_distance(max, INTERNAL_ORIGIN) > EXTENT_DISTANCE):
        output.print_md('BAD_STRG' + 
        '3D View Bounding Box extends more than 10 Mi (16KM) away from the Internal Origin.')
    else:
        output.print_md('GOOD_STRG' + 
        '3D View Bounding Box is located less than 10 Mi (16KM) away from the Internal Origin.')
        test_score += 1
    # _____________________________________________Get Objects in Design Options
    print("")
    print(divider)
    output.print_md('# Checking the extents of the design option objects')
    print(divider)
    design_option_objects = get_design_options_elements(document)
    violating_design_option_objects = []
    violating_options = []
    for x in design_option_objects[1]:
        for y in x:
            dbbox = y.get_BoundingBox(None)
            if dbbox is None:
                continue
            else:
                dbmin = (dbbox.Min.X, dbbox.Min.Y, dbbox.Min.Z)
                dbmax = (dbbox.Max.X, dbbox.Max.Y, dbbox.Max.Z)
                if calculate_distance(
                    (dbmin, INTERNAL_ORIGIN) > EXTENT_DISTANCE or 
                    calculate_distance(
                        dbmax, INTERNAL_ORIGIN) > EXTENT_DISTANCE):
                    violating_design_option_objects.append(x)
                    if y.DesignOption.Name not in violating_options:
                        violating_options.append(y.DesignOption.Name)
    if len(violating_design_option_objects) > 0:
        output.print_md('BAD_STRG' + 
        'Design Option Objects are located more than 10 Mi (16KM) away from the Internal Origin.')
        if len(violating_design_option_objects) > 10:
            output.print_md('WARN_STRGShowing the first 10 objects')
            output.print_md('WARN_STRGManual investigation is required')
        counter = 0
        limit = 10
        for x in violating_design_option_objects:

            for y in x:
                if counter == limit:
                    break
                print(output.linkify(y.Id) + 
                            str(y.Name) +
                            " - Is part of design option - "
                            + str(y.DesignOption.Name))
                counter += 1
    else:
        output.print_md('GOOD_STRG' + 
        'No object in any design option is located more than 10 Mi (16KM) away from the Internal Origin.')
        test_score += 1
    # __________________________________________________________Check Test Score
    if test_score >= 2:
        output.print_md('GOOD_STRGAll Tests Passed.')
        script.exit()
    else:
        output.print_md('BAD_STRG' + 
        'Distant objects detected, Proceeding with additional analysis')
    # ___________________________________________________Check CAD and RVT Links
    print(divider)
    output.print_md('# Checking the extents of the CAD and RVT links')
    print(divider)
    bboxLink = bbox_instance.get_tempbbox(1, 1, 1, 0)
    badcads = bboxLink[1]
    badrvts = bboxLink[2]
    cleanbbox = bboxLink[3]
    # print (bboxLink[1], bboxLink[2])
    # print(bbox.Min, cleanbbox.Min)
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
        output.print_md('GOOD_STRG' +
        'All CAD and RVT Links are located less than 10 Mi (16KM) away from the Internal Origin.')
        test_score += 1
        print(divider)
    if check_bounding_box(cleanbbox, INTERNAL_ORIGIN, 5) == 0:
        output.print_md('BAD_STRG' + 
        'Distant objects are still being detected!')
        output.print_md('WARN_STRG' + 
        'Further Analysis Required.')
    else:
        output.print_md('GOOD_STRG' + 
        'All Objects are located less than 10 Mi (16KM) away from the Internal Origin.')
        script.exit()
    print(divider)
    output.print_md('# Checking everything, It is going to take a while.')
    output.print_md('# Please be patient.')
    # __________________________Check Bounding Box of Every Element in the Model
    print(divider)
    getbadelements = bbox_instance.get_tempbbox(0,0,0,1)
    badelements = getbadelements[4]
    counter = 0
    limit = 10
    if len(badelements) > 0:
        if len(badelements) > limit:
            output.print_md('WARN_STRG' + 
            'Showing the first 10 objects')
            output.print_md('WARN_STRG' + 
            'Manual investigation is required')
        output.print_md('BAD_STRG' + 
        'Elements below are located more than 10 Mi (16KM) away from the Internal Origin')
        for x in badelements:
            print(output.linkify(x.Id)+ '  ' + 
                    str(x.Name) + '  ' + str(x.Category.Name))
            if counter == limit:
                break
            counter += 1
    else:
        output.print_md('GOOD_STRG' + 
        'All Objects are located less than 10 Mi (16KM) away from the Internal Origin.')
        test_score += 1


# ______________________________________________Model Checker Class
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
        check_model_extents(doc)

    def tearDown(self, doc, output):
        pass

    def doCleanups(self, doc, output):
        pass
