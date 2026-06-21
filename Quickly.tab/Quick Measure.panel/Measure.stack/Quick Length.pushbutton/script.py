# -*- coding: utf-8 -*-
"""Quick Length - Sum lengths of selected Revit elements with unit conversion.

Reads length from walls, model lines, detail lines, line-based families,
and any element containing a length parameter. Displays total with
configurable units, precision, category filtering, element breakdown,
and live-selection mode via a modeless window.
"""
__title__ = "Quick\nLength"
__doc__ = "Sum the total length of selected elements with unit conversion"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

# Persistent engine keeps the script alive for the modeless window.
__persistentengine__ = True

import os

from Autodesk.Revit.DB import BuiltInParameter, LocationCurve
from pyrevit import DB

from quickmeasure import QuantitySpec, launch

SCRIPT_DIR = os.path.dirname(__file__)


def extract_length(element):
    """Length in internal units (feet), or None. Prefers LocationCurve."""
    try:
        loc = element.Location
        if isinstance(loc, LocationCurve) and loc.Curve:
            length = loc.Curve.Length
            return length if length > 0 else None
    except Exception:
        pass
    for source in (BuiltInParameter.CURVE_ELEM_LENGTH, "Length", "Curve Length"):
        try:
            if isinstance(source, str):
                param = element.LookupParameter(source)
            else:
                param = element.get_Parameter(source)
            if param and param.HasValue and param.AsDouble() > 0:
                return param.AsDouble()
        except Exception:
            pass
    return None


SPEC = QuantitySpec(
    name="Length",
    noun="length",
    xaml_path=os.path.join(SCRIPT_DIR, "QuickLength.xaml"),
    config_filename="quick_length_config.xml",
    imperial_units=["Fractional Feet and Inches", "Decimal Feet", "Decimal Inches"],
    metric_units=["Meters", "Centimeters", "Millimeters"],
    imperial_precisions=[
        ('1/256"', 1.0 / 256),
        ('1/128"', 1.0 / 128),
        ('1/64"', 1.0 / 64),
        ('1/32"', 1.0 / 32),
        ('1/16"', 1.0 / 16),
        ('1/8"', 1.0 / 8),
        ('1/4"', 1.0 / 4),
        ('1/2"', 1.0 / 2),
        ('1"', 1.0),
        ("1'", 12.0),
    ],
    metric_precisions=[
        ("1 mm", 1.0),
        ("1 cm", 10.0),
        ("1 m", 1000.0),
    ],
    unit_suffixes={
        "Fractional Feet and Inches": "",
        "Decimal Feet": " ft",
        "Decimal Inches": " in",
        "Meters": " m",
        "Centimeters": " cm",
        "Millimeters": " mm",
    },
    spec_type_id=DB.SpecTypeId.Length,
    forge_map={
        "autodesk.unit.unit:feetFractionalInches": "Fractional Feet and Inches",
        "autodesk.unit.unit:feet": "Decimal Feet",
        "autodesk.unit.unit:inches": "Decimal Inches",
        "autodesk.unit.unit:meters": "Meters",
        "autodesk.unit.unit:centimeters": "Centimeters",
        "autodesk.unit.unit:millimeters": "Millimeters",
    },
    default_unit="Decimal Feet",
    default_imperial_prec_idx=4,
    default_metric_prec_idx=0,
    extract=extract_length,
    formatter="length",
)

launch(SPEC)
