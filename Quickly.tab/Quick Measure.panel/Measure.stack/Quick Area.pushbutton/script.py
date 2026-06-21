# -*- coding: utf-8 -*-
"""Quick Area - Sum areas of selected Revit elements with unit conversion.

Reads area from floors, roofs, rooms, walls, ceilings, filled regions,
masking regions, area plan elements, and any element containing an area
parameter. Displays total with configurable units, precision, category
filtering, element breakdown, and live-selection mode via a modeless window.
"""
__title__ = "Quick\nArea"
__doc__ = "Sum the total area of selected elements with unit conversion"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

# Persistent engine keeps the script alive for the modeless window.
__persistentengine__ = True

import os

from Autodesk.Revit.DB import BuiltInParameter
from pyrevit import DB

from quickmeasure import QuantitySpec, launch

SCRIPT_DIR = os.path.dirname(__file__)
SUP2 = u"²"

# Built-in area parameters to try first (geometric truth), in priority order.
AREA_BIP_LIST = [
    BuiltInParameter.HOST_AREA_COMPUTED,   # floors, roofs, ceilings, walls
    BuiltInParameter.ROOM_AREA,            # rooms
]


def extract_area(element):
    """Area in internal units (sq ft), or None. Prefers computed host area."""
    for bip in AREA_BIP_LIST:
        try:
            param = element.get_Parameter(bip)
            if param and param.HasValue and param.AsDouble() > 0:
                return param.AsDouble()
        except Exception:
            pass
    for pname in ("Area", "Surface Area", "Filled Area"):
        try:
            param = element.LookupParameter(pname)
            if param and param.HasValue and param.AsDouble() > 0:
                return param.AsDouble()
        except Exception:
            pass
    return None


SPEC = QuantitySpec(
    name="Area",
    noun="area",
    xaml_path=os.path.join(SCRIPT_DIR, "QuickArea.xaml"),
    config_filename="quick_area_config.xml",
    imperial_units=["Square Feet", "Square Inches", "Acres"],
    metric_units=["Square Meters", "Square Centimeters", "Square Millimeters"],
    imperial_precisions=[
        ("0.001 ft" + SUP2, 0.001),
        ("0.01 ft" + SUP2, 0.01),
        ("0.1 ft" + SUP2, 0.1),
        ("1 ft" + SUP2, 1.0),
        ("10 ft" + SUP2, 10.0),
        ("100 ft" + SUP2, 100.0),
    ],
    metric_precisions=[
        ("1 mm" + SUP2, 0.000001),
        ("1 cm" + SUP2, 0.0001),
        ("0.01 m" + SUP2, 0.01),
        ("0.1 m" + SUP2, 0.1),
        ("1 m" + SUP2, 1.0),
    ],
    unit_suffixes={
        "Square Feet": " ft" + SUP2,
        "Square Inches": " in" + SUP2,
        "Acres": " ac",
        "Square Meters": " m" + SUP2,
        "Square Centimeters": " cm" + SUP2,
        "Square Millimeters": " mm" + SUP2,
    },
    spec_type_id=DB.SpecTypeId.Area,
    forge_map={
        "autodesk.unit.unit:squareFeet": "Square Feet",
        "autodesk.unit.unit:squareInches": "Square Inches",
        "autodesk.unit.unit:acres": "Acres",
        "autodesk.unit.unit:squareMeters": "Square Meters",
        "autodesk.unit.unit:squareCentimeters": "Square Centimeters",
        "autodesk.unit.unit:squareMillimeters": "Square Millimeters",
    },
    default_unit="Square Feet",
    default_imperial_prec_idx=2,
    default_metric_prec_idx=2,
    extract=extract_area,
    formatter="decimal",
    conversions={
        "Square Feet": 1.0,
        "Square Inches": 144.0,
        "Acres": 1.0 / 43560.0,
        "Square Meters": 0.09290304,
        "Square Centimeters": 929.0304,
        "Square Millimeters": 92903.04,
    },
    prec_display_multipliers={
        "Square Feet": 1.0,
        "Square Inches": 144.0,
        "Acres": 1.0 / 43560.0,
        "Square Meters": 1.0,
        "Square Centimeters": 10000.0,
        "Square Millimeters": 1000000.0,
    },
)

launch(SPEC)
