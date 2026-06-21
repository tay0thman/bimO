# -*- coding: utf-8 -*-
"""Quick Volume - Sum volumes of selected Revit elements with unit conversion.

Reads volume from walls, floors, roofs, ceilings, rooms, and any element
containing a volume parameter (with a geometry-based fallback). Displays total
with configurable units, precision, category filtering, element breakdown, and
live-selection mode via a modeless window.
"""
__title__ = "Quick\nVolume"
__doc__ = "Sum the total volume of selected elements with unit conversion"
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
SUP3 = u"³"

VOLUME_BIP_LIST = [
    BuiltInParameter.HOST_VOLUME_COMPUTED,   # walls, floors, roofs, ceilings
    BuiltInParameter.ROOM_VOLUME,            # rooms
]


def extract_volume(element):
    """Volume in internal units (cu ft), or None. Prefers computed host volume."""
    for bip in VOLUME_BIP_LIST:
        try:
            param = element.get_Parameter(bip)
            if param and param.HasValue and param.AsDouble() > 0:
                return param.AsDouble()
        except Exception:
            pass
    try:
        param = element.LookupParameter("Volume")
        if param and param.HasValue and param.AsDouble() > 0:
            return param.AsDouble()
    except Exception:
        pass
    # Geometry-based fallback: sum solid volumes.
    try:
        geom = element.get_Geometry(DB.Options())
        if geom:
            total = 0.0
            for geom_obj in geom:
                if hasattr(geom_obj, "Volume") and geom_obj.Volume > 0:
                    total += geom_obj.Volume
                elif hasattr(geom_obj, "GetInstanceGeometry"):
                    inst = geom_obj.GetInstanceGeometry()
                    if inst:
                        for sub in inst:
                            if hasattr(sub, "Volume") and sub.Volume > 0:
                                total += sub.Volume
            if total > 0:
                return total
    except Exception:
        pass
    return None


SPEC = QuantitySpec(
    name="Volume",
    noun="volume",
    xaml_path=os.path.join(SCRIPT_DIR, "QuickVolume.xaml"),
    config_filename="quick_volume_config.xml",
    imperial_units=["Cubic Feet", "Cubic Inches", "Cubic Yards"],
    metric_units=["Cubic Meters", "Liters", "Cubic Centimeters"],
    imperial_precisions=[
        ("0.001 ft" + SUP3, 0.001),
        ("0.01 ft" + SUP3, 0.01),
        ("0.1 ft" + SUP3, 0.1),
        ("1 ft" + SUP3, 1.0),
        ("10 ft" + SUP3, 10.0),
        ("100 ft" + SUP3, 100.0),
    ],
    metric_precisions=[
        ("1 cm" + SUP3, 0.000001),
        ("1 L", 0.001),
        ("0.01 m" + SUP3, 0.01),
        ("0.1 m" + SUP3, 0.1),
        ("1 m" + SUP3, 1.0),
    ],
    unit_suffixes={
        "Cubic Feet": " ft" + SUP3,
        "Cubic Inches": " in" + SUP3,
        "Cubic Yards": " yd" + SUP3,
        "Cubic Meters": " m" + SUP3,
        "Liters": " L",
        "Cubic Centimeters": " cm" + SUP3,
    },
    spec_type_id=DB.SpecTypeId.Volume,
    forge_map={
        "autodesk.unit.unit:cubicFeet": "Cubic Feet",
        "autodesk.unit.unit:cubicInches": "Cubic Inches",
        "autodesk.unit.unit:cubicYards": "Cubic Yards",
        "autodesk.unit.unit:cubicMeters": "Cubic Meters",
        "autodesk.unit.unit:liters": "Liters",
        "autodesk.unit.unit:cubicCentimeters": "Cubic Centimeters",
    },
    default_unit="Cubic Feet",
    default_imperial_prec_idx=2,
    default_metric_prec_idx=2,
    extract=extract_volume,
    formatter="decimal",
    conversions={
        "Cubic Feet": 1.0,
        "Cubic Inches": 1728.0,
        "Cubic Yards": 1.0 / 27.0,
        "Cubic Meters": 0.028316846592,
        "Liters": 28.316846592,
        "Cubic Centimeters": 28316.846592,
    },
    prec_display_multipliers={
        "Cubic Feet": 1.0,
        "Cubic Inches": 1728.0,
        "Cubic Yards": 1.0 / 27.0,
        "Cubic Meters": 1.0,
        "Liters": 1000.0,
        "Cubic Centimeters": 1000000.0,
    },
)

launch(SPEC)
