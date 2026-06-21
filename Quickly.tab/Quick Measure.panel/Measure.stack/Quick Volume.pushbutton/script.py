# -*- coding: utf-8 -*-
"""Quick Volume - Sum volumes of selected Revit elements with unit conversion.

Reads volume from walls, floors, roofs, ceilings, rooms, columns,
beams, foundations, and any element containing a volume parameter.
Displays total with configurable units, precision, category filtering,
element breakdown, and live-selection mode via modeless window.
"""
__title__ = "Quick\nVolume"
__doc__ = "Sum the total volume of selected elements with unit conversion"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

# Persistent engine keeps the script alive for the modeless window
__persistentengine__ = True

# =============================================================================
# IMPORTS
# =============================================================================
import clr
import os
import math
import time

clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System")
clr.AddReference("System.Xml")

from System.Windows import (
    Window,
    Visibility,
)
from System.Windows.Controls.Primitives import ToggleButton
from System.Windows.Input import ApplicationCommands
from System.Windows.Markup import XamlReader
from System.Windows.Media.Animation import (
    DoubleAnimation,
    FillBehavior,
)
from System.IO import StringReader
from System.Xml import XmlReader as SysXmlReader
from System.Windows import Clipboard as WinClipboard, Duration
from System import TimeSpan

import xml.etree.ElementTree as ET

from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementId,
)
from Autodesk.Revit.UI import (
    IExternalEventHandler,
    ExternalEvent,
)

from pyrevit import revit, DB, script

logger = script.get_logger()
output = script.get_output()


# =============================================================================
# CONSTANTS
# =============================================================================
SCRIPT_DIR = os.path.dirname(__file__)
XAML_PATH = os.path.join(SCRIPT_DIR, "QuickVolume.xaml")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "quick_volume_config.xml")

APPDATA_DIR = os.path.join(
    os.environ.get("APPDATA", ""),
    "pyRevit",
    "Quickly",
)
APPDATA_CONFIG_PATH = os.path.join(APPDATA_DIR, "quick_volume_config.xml")

SUP3 = u"\u00B3"

IMPERIAL_UNITS = [
    "Cubic Feet",
    "Cubic Inches",
    "Cubic Yards",
]

METRIC_UNITS = [
    "Cubic Meters",
    "Liters",
    "Cubic Centimeters",
]

ALL_UNITS = IMPERIAL_UNITS + METRIC_UNITS

# Precision steps: (label, value_in_base_unit)
# Imperial base: cubic feet
IMPERIAL_PRECISIONS = [
    ("0.001 ft" + SUP3, 0.001),
    ("0.01 ft" + SUP3,  0.01),
    ("0.1 ft" + SUP3,   0.1),
    ("1 ft" + SUP3,     1.0),
    ("10 ft" + SUP3,    10.0),
    ("100 ft" + SUP3,   100.0),
]

# Metric base: cubic meters
METRIC_PRECISIONS = [
    ("1 cm" + SUP3,    0.000001),
    ("1 L",            0.001),
    ("0.01 m" + SUP3,  0.01),
    ("0.1 m" + SUP3,   0.1),
    ("1 m" + SUP3,     1.0),
]

UNIT_SUFFIXES = {
    "Cubic Feet":        " ft" + SUP3,
    "Cubic Inches":      " in" + SUP3,
    "Cubic Yards":       " yd" + SUP3,
    "Cubic Meters":      " m" + SUP3,
    "Liters":            " L",
    "Cubic Centimeters": " cm" + SUP3,
}

# Conversion factors from internal cubic feet
CUFT_CONVERSIONS = {
    "Cubic Feet":        1.0,
    "Cubic Inches":      1728.0,
    "Cubic Yards":       1.0 / 27.0,
    "Cubic Meters":      0.028316846592,
    "Liters":            28.316846592,
    "Cubic Centimeters": 28316.846592,
}

# Precision base-unit to display-unit multipliers
# Imperial precisions are in cu ft; metric precisions are in cu m
PREC_DISPLAY_MULTIPLIERS = {
    "Cubic Feet":        1.0,                   # cu ft -> cu ft
    "Cubic Inches":      1728.0,                # cu ft -> cu in
    "Cubic Yards":       1.0 / 27.0,            # cu ft -> cu yd
    "Cubic Meters":      1.0,                   # cu m -> cu m
    "Liters":            1000.0,                # cu m -> L
    "Cubic Centimeters": 1000000.0,             # cu m -> cu cm
}

LARGE_SELECTION_THRESHOLD = 500

# Built-in parameters to try for volume extraction
VOLUME_BIP_LIST = [
    BuiltInParameter.HOST_VOLUME_COMPUTED,      # Walls, floors, roofs, ceilings
    BuiltInParameter.ROOM_VOLUME,               # Rooms
]


# =============================================================================
# SINGLETON WINDOW TRACKING
# =============================================================================
_active_window = None


def _get_active_window():
    global _active_window
    return _active_window


def _set_active_window(win):
    global _active_window
    _active_window = win


# =============================================================================
# DATA CLASS
# =============================================================================
class ElementRow(object):
    """Data row for the breakdown DataGrid."""
    def __init__(self, element_id, category, family_type, vol_cuft):
        self.element_id = element_id
        self.category = category
        self.family_type = family_type
        self.vol_cuft = vol_cuft
        self.vol_str = ""

    @property
    def ElementId(self):
        return str(self.element_id)

    @property
    def Category(self):
        return self.category

    @property
    def FamilyType(self):
        return self.family_type

    @property
    def Volume(self):
        return self.vol_str


# =============================================================================
# HELPERS
# =============================================================================
def is_imperial(unit_name):
    return unit_name in IMPERIAL_UNITS


def get_precisions(unit_name):
    if is_imperial(unit_name):
        return IMPERIAL_PRECISIONS
    return METRIC_PRECISIONS


def get_element_id_int(el):
    try:
        return el.Id.Value
    except AttributeError:
        return el.Id.IntegerValue


def get_element_category_name(element):
    try:
        if element.Category:
            return element.Category.Name
    except Exception:
        pass
    return "Unknown"


def get_element_family_type(element):
    try:
        doc = element.Document
        type_id = element.GetTypeId()
        if type_id and type_id != ElementId.InvalidElementId:
            el_type = doc.GetElement(type_id)
            if el_type:
                family_name = ""
                try:
                    family_name = el_type.FamilyName
                except Exception:
                    pass
                type_name = ""
                try:
                    pname = el_type.get_Parameter(
                        BuiltInParameter.ALL_MODEL_TYPE_NAME
                    )
                    if pname and pname.HasValue:
                        type_name = pname.AsString()
                    else:
                        type_name = getattr(el_type, "Name", "")
                except Exception:
                    type_name = getattr(el_type, "Name", "")

                if family_name and type_name:
                    return "{0} : {1}".format(family_name, type_name)
                return family_name or type_name or u"\u2014"
    except Exception:
        pass
    try:
        return element.Name or u"\u2014"
    except Exception:
        return u"\u2014"


# =============================================================================
# VOLUME EXTRACTION
# =============================================================================
def get_element_volume(element):
    """Extract volume from a Revit element in internal units (cu ft).

    Tries built-in volume parameters first, then falls back to
    LookupParameter("Volume").
    """
    # Strategy 1: Built-in volume parameters (geometric truth)
    for bip in VOLUME_BIP_LIST:
        try:
            param = element.get_Parameter(bip)
            if param and param.HasValue:
                val = param.AsDouble()
                if val > 0:
                    return val
        except Exception:
            pass

    # Strategy 2: "Volume" parameter by name
    try:
        param = element.LookupParameter("Volume")
        if param and param.HasValue:
            val = param.AsDouble()
            if val > 0:
                return val
    except Exception:
        pass

    # Strategy 3: Geometry-based volume via solid extraction
    try:
        opt = DB.Options()
        geom = element.get_Geometry(opt)
        if geom:
            total_vol = 0.0
            for geom_obj in geom:
                if hasattr(geom_obj, "Volume") and geom_obj.Volume > 0:
                    total_vol += geom_obj.Volume
                elif hasattr(geom_obj, "GetInstanceGeometry"):
                    inst_geom = geom_obj.GetInstanceGeometry()
                    if inst_geom:
                        for sub in inst_geom:
                            if (hasattr(sub, "Volume")
                                    and sub.Volume > 0):
                                total_vol += sub.Volume
            if total_vol > 0:
                return total_vol
    except Exception:
        pass

    return None


def collect_element_data(elements):
    """Build ElementRow list. Returns (rows, skipped_count)."""
    rows = []
    skipped = 0
    t0 = time.time()

    for i, el in enumerate(elements):
        vol = get_element_volume(el)
        if vol is None or vol <= 0:
            skipped += 1
            if vol is not None and vol <= 0:
                logger.debug(
                    "Quick Volume: Skipped element {0} — "
                    "non-positive volume ({1})".format(el.Id, vol)
                )
            continue

        row = ElementRow(
            element_id=get_element_id_int(el),
            category=get_element_category_name(el),
            family_type=get_element_family_type(el),
            vol_cuft=vol,
        )
        rows.append(row)

        if (len(elements) > LARGE_SELECTION_THRESHOLD
                and (i + 1) % 500 == 0):
            elapsed = time.time() - t0
            logger.debug(
                "Quick Volume: Processed {0}/{1} elements ({2:.1f}s)"
                .format(i + 1, len(elements), elapsed)
            )

    elapsed = time.time() - t0
    if elapsed > 1.0:
        logger.debug(
            "Quick Volume: Total processing {0:.2f}s for {1} elements"
            .format(elapsed, len(elements))
        )
    if skipped > 0:
        logger.debug(
            "Quick Volume: Skipped {0} element(s) with no valid volume"
            .format(skipped)
        )

    return rows, skipped


# =============================================================================
# PROJECT UNIT DETECTION
# =============================================================================
def detect_project_unit():
    """Detect the current Revit project display unit for volume."""
    doc = revit.doc
    try:
        units = doc.GetUnits()

        # New API (Revit 2022+)
        try:
            spec_vol = DB.SpecTypeId.Volume
            fo = units.GetFormatOptions(spec_vol)
            uid = fo.GetUnitTypeId()
            forge_map = {
                "autodesk.unit.unit:cubicFeet":
                    "Cubic Feet",
                "autodesk.unit.unit:cubicInches":
                    "Cubic Inches",
                "autodesk.unit.unit:cubicYards":
                    "Cubic Yards",
                "autodesk.unit.unit:cubicMeters":
                    "Cubic Meters",
                "autodesk.unit.unit:liters":
                    "Liters",
                "autodesk.unit.unit:cubicCentimeters":
                    "Cubic Centimeters",
            }
            type_id_str = uid.TypeId if hasattr(uid, "TypeId") else str(uid)
            for key, val in forge_map.items():
                if key in type_id_str:
                    return val
        except Exception:
            pass

        # Legacy API (Revit < 2022)
        try:
            fo = units.GetFormatOptions(DB.UnitType.UT_Volume)
            du = fo.DisplayUnits
            legacy_map = {
                DB.DisplayUnitType.DUT_CUBIC_FEET:
                    "Cubic Feet",
                DB.DisplayUnitType.DUT_CUBIC_INCHES:
                    "Cubic Inches",
                DB.DisplayUnitType.DUT_CUBIC_YARDS:
                    "Cubic Yards",
                DB.DisplayUnitType.DUT_CUBIC_METERS:
                    "Cubic Meters",
                DB.DisplayUnitType.DUT_LITERS:
                    "Liters",
                DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS:
                    "Cubic Centimeters",
            }
            return legacy_map.get(du, "Cubic Feet")
        except Exception:
            pass
    except Exception:
        pass
    return "Cubic Feet"


def get_project_guid():
    doc = revit.doc
    try:
        return str(doc.ProjectInformation.UniqueId)
    except Exception:
        pass
    try:
        if doc.PathName:
            import hashlib
            return hashlib.md5(doc.PathName.encode("utf-8")).hexdigest()
    except Exception:
        pass
    return "default"


# =============================================================================
# UNIT CONVERSION & FORMATTING
# =============================================================================
def cuft_to_raw(total_cuft, unit_name):
    return total_cuft * CUFT_CONVERSIONS.get(unit_name, 1.0)


def format_decimal(value, precision_in_display_unit, suffix):
    if precision_in_display_unit <= 0:
        precision_in_display_unit = 0.001
    rounded = round(value / precision_in_display_unit) * precision_in_display_unit

    if precision_in_display_unit >= 1.0:
        decimal_places = 0
    else:
        decimal_places = max(
            0, int(math.ceil(-math.log10(precision_in_display_unit)))
        )
        decimal_places = min(decimal_places, 8)

    fmt = "{{0:.{0}f}}{{1}}".format(decimal_places)
    return fmt.format(rounded, suffix)


def format_volume(total_cuft, unit_name, precision_index):
    """Master formatting function. Returns a display string."""
    precisions = get_precisions(unit_name)
    idx = max(0, min(precision_index, len(precisions) - 1))

    raw = cuft_to_raw(total_cuft, unit_name)
    prec_base = precisions[idx][1]

    prec_display = prec_base * PREC_DISPLAY_MULTIPLIERS.get(unit_name, 1.0)

    suffix = UNIT_SUFFIXES.get(unit_name, "")
    return format_decimal(raw, prec_display, suffix)


# =============================================================================
# CONFIG PERSISTENCE
# =============================================================================
def _resolve_config_path():
    try:
        test_file = os.path.join(SCRIPT_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return CONFIG_PATH
    except Exception:
        pass
    try:
        if not os.path.exists(APPDATA_DIR):
            os.makedirs(APPDATA_DIR)
        return APPDATA_CONFIG_PATH
    except Exception:
        return CONFIG_PATH


def load_config(project_guid):
    config_path = _resolve_config_path()
    try:
        if os.path.exists(config_path):
            tree = ET.parse(config_path)
            root = tree.getroot()
            projects_el = root.find("Projects")
            if projects_el is not None:
                for proj in projects_el.findall("Project"):
                    if proj.get("guid") == project_guid:
                        unit = proj.find("SelectedUnit").text
                        prec = int(proj.find("PrecisionIndex").text)
                        if unit in ALL_UNITS:
                            return unit, prec
                for proj in projects_el.findall("Project"):
                    if proj.get("guid") == "default":
                        unit = proj.find("SelectedUnit").text
                        prec = int(proj.find("PrecisionIndex").text)
                        if unit in ALL_UNITS:
                            return unit, prec
    except Exception as ex:
        logger.debug("Quick Volume: Could not load config — {0}".format(ex))
    return None, None


def save_config(project_guid, unit_name, precision_index):
    config_path = _resolve_config_path()
    try:
        if os.path.exists(config_path):
            try:
                tree = ET.parse(config_path)
                root = tree.getroot()
            except Exception:
                root = ET.Element("QuickVolumeConfig")
                tree = ET.ElementTree(root)
        else:
            root = ET.Element("QuickVolumeConfig")
            tree = ET.ElementTree(root)

        projects_el = root.find("Projects")
        if projects_el is None:
            projects_el = ET.SubElement(root, "Projects")

        target = None
        for proj in projects_el.findall("Project"):
            if proj.get("guid") == project_guid:
                target = proj
                break
        if target is None:
            target = ET.SubElement(projects_el, "Project")
            target.set("guid", project_guid)

        unit_el = target.find("SelectedUnit")
        if unit_el is None:
            unit_el = ET.SubElement(target, "SelectedUnit")
        unit_el.text = unit_name

        prec_el = target.find("PrecisionIndex")
        if prec_el is None:
            prec_el = ET.SubElement(target, "PrecisionIndex")
        prec_el.text = str(precision_index)

        tree.write(config_path, encoding="utf-8", xml_declaration=True)
    except Exception as ex:
        logger.warning(
            "Quick Volume: Could not save config — {0}".format(ex)
        )


# =============================================================================
# EXTERNAL EVENT HANDLER
# =============================================================================
class SelectionUpdateHandler(IExternalEventHandler):
    def __init__(self):
        self.window = None

    def Execute(self, uiapp):
        if self.window is None:
            return
        try:
            self.window.refresh_from_selection()
        except Exception as ex:
            logger.debug(
                "Quick Volume live update error: {0}".format(ex)
            )

    def GetName(self):
        return "QuickVolumeSelectionUpdate"


# =============================================================================
# WPF MODELESS WINDOW CONTROLLER
# =============================================================================
class QuickVolumeWindow(object):

    def __init__(self, ext_event, ext_handler):
        self.ext_event = ext_event
        self.ext_handler = ext_handler
        self.ext_handler.window = self

        self.project_guid = get_project_guid()

        self._updating = False
        self._all_rows = []
        self._categories = {}
        self._active_categories = set()
        self._chip_buttons = {}
        self._live_timer = None

        self._load_xaml()
        self._init_controls()
        self._bind_events()
        self.refresh_from_selection()

    def _load_xaml(self):
        with open(XAML_PATH, "r") as f:
            xaml_str = f.read()
        string_reader = StringReader(xaml_str)
        xml_reader = SysXmlReader.Create(string_reader)
        self.window = XamlReader.Load(xml_reader)

    def _init_controls(self):
        self.txt_output = self.window.FindName("txt_output")
        self.btn_copy = self.window.FindName("btn_copy")
        self.btn_refresh = self.window.FindName("btn_refresh")
        self.tgl_live = self.window.FindName("tgl_live")
        self.cmb_unit = self.window.FindName("cmb_unit")
        self.sld_precision = self.window.FindName("sld_precision")
        self.txt_precision = self.window.FindName("txt_precision")
        self.txt_status = self.window.FindName("txt_status")
        self.pnl_filters = self.window.FindName("pnl_filters")
        self.brd_filters = self.window.FindName("brd_filters")
        self.tgl_breakdown = self.window.FindName("tgl_breakdown")
        self.brd_breakdown = self.window.FindName("brd_breakdown")
        self.dgd_elements = self.window.FindName("dgd_elements")
        self.brd_toast = self.window.FindName("brd_toast")
        self.txt_toast = self.window.FindName("txt_toast")

        for unit in ALL_UNITS:
            self.cmb_unit.Items.Add(unit)

        saved_unit, saved_prec = load_config(self.project_guid)
        if saved_unit is None:
            saved_unit = detect_project_unit()
            if saved_unit not in ALL_UNITS:
                saved_unit = ALL_UNITS[0]
        if saved_prec is None:
            saved_prec = 2

        self._updating = True
        self.cmb_unit.SelectedItem = saved_unit
        self._configure_slider(saved_unit, saved_prec)
        self._updating = False

    def _configure_slider(self, unit_name, prec_index=None):
        precisions = get_precisions(unit_name)
        max_val = len(precisions) - 1
        self.sld_precision.Minimum = 0
        self.sld_precision.Maximum = max_val
        if prec_index is not None:
            idx = max(0, min(prec_index, max_val))
        else:
            idx = int(self.sld_precision.Value)
            idx = max(0, min(idx, max_val))
        self.sld_precision.Value = idx
        self._update_precision_label()

    def _bind_events(self):
        self.cmb_unit.SelectionChanged += self._on_unit_changed
        self.sld_precision.ValueChanged += self._on_precision_changed
        self.btn_copy.Click += self._on_copy_click
        self.btn_refresh.Click += self._on_refresh_click
        self.tgl_live.Checked += self._on_live_toggled
        self.tgl_live.Unchecked += self._on_live_toggled
        self.tgl_breakdown.Checked += self._on_breakdown_toggled
        self.tgl_breakdown.Unchecked += self._on_breakdown_toggled
        self.dgd_elements.SelectionChanged += self._on_grid_selection
        self.window.Closed += self._on_closed
        copy_binding = self.window.CommandBindings[0]
        copy_binding.Executed += self._on_copy_command

    # -----------------------------------------------------------------
    # Selection Refresh
    # -----------------------------------------------------------------
    def refresh_from_selection(self):
        selection = revit.get_selection()
        elements = selection.elements if selection else []
        selected_count = len(elements)

        rows, skipped = collect_element_data(elements)

        self._all_rows = rows
        self._build_categories()
        self._build_filter_chips()
        self._update_display()
        self._update_grid()
        self._update_status(selected_count, len(rows), skipped)

    def _build_categories(self):
        self._categories = {}
        for row in self._all_rows:
            cat = row.category
            if cat not in self._categories:
                self._categories[cat] = []
            self._categories[cat].append(row)
        self._active_categories = set(self._categories.keys())

    def _build_filter_chips(self):
        self.pnl_filters.Children.Clear()
        self._chip_buttons = {}
        if len(self._categories) < 2:
            self.brd_filters.Visibility = Visibility.Collapsed
            return
        self.brd_filters.Visibility = Visibility.Visible
        sorted_cats = sorted(self._categories.keys())
        for cat in sorted_cats:
            count = len(self._categories[cat])
            chip = ToggleButton()
            chip.Content = "{0} ({1})".format(cat, count)
            chip.IsChecked = True
            chip.Style = self.window.FindResource("ChipToggleStyle")
            chip.Checked += self._on_chip_toggled
            chip.Unchecked += self._on_chip_toggled
            chip.Tag = cat
            self.pnl_filters.Children.Add(chip)
            self._chip_buttons[cat] = chip

    def _get_filtered_rows(self):
        if not self._active_categories:
            return self._all_rows
        return [r for r in self._all_rows
                if r.category in self._active_categories]

    def _get_filtered_total(self):
        return sum(r.vol_cuft for r in self._get_filtered_rows())

    # -----------------------------------------------------------------
    # Event Handlers
    # -----------------------------------------------------------------
    def _on_unit_changed(self, sender, args):
        if self._updating:
            return
        self._updating = True
        unit_name = self.cmb_unit.SelectedItem
        if unit_name:
            old_is_imp = True
            if args.RemovedItems.Count > 0:
                old_is_imp = is_imperial(args.RemovedItems[0])
            new_is_imp = is_imperial(unit_name)
            if old_is_imp != new_is_imp:
                self._configure_slider(unit_name, 2)
            else:
                self._configure_slider(unit_name)
        self._updating = False
        self._update_display()
        self._update_grid()

    def _on_precision_changed(self, sender, args):
        if self._updating:
            return
        self._update_precision_label()
        self._update_display()
        self._update_grid()

    def _on_copy_click(self, sender, args):
        self._do_copy()

    def _on_copy_command(self, sender, args):
        self._do_copy()

    def _on_refresh_click(self, sender, args):
        try:
            self.ext_event.Raise()
        except Exception:
            self.refresh_from_selection()

    def _on_live_toggled(self, sender, args):
        if self.tgl_live.IsChecked:
            self._start_live_polling()
        else:
            self._stop_live_polling()

    def _on_chip_toggled(self, sender, args):
        self._active_categories = set()
        for cat, chip in self._chip_buttons.items():
            if chip.IsChecked:
                self._active_categories.add(cat)
        self._update_display()
        self._update_grid()

    def _on_breakdown_toggled(self, sender, args):
        if self.tgl_breakdown.IsChecked:
            self.tgl_breakdown.Content = \
                u"\u25BC Hide Element Breakdown"
            self.brd_breakdown.Visibility = Visibility.Visible
        else:
            self.tgl_breakdown.Content = \
                u"\u25B6 Show Element Breakdown"
            self.brd_breakdown.Visibility = Visibility.Collapsed

    def _on_grid_selection(self, sender, args):
        try:
            selected_item = self.dgd_elements.SelectedItem
            if selected_item and hasattr(selected_item, "element_id"):
                try:
                    eid = ElementId(int(selected_item.element_id))
                except Exception:
                    eid = ElementId(selected_item.element_id)
                uidoc = revit.uidoc
                sel = uidoc.Selection
                from System.Collections.Generic import List
                id_list = List[ElementId]()
                id_list.Add(eid)
                sel.SetElementIds(id_list)
        except Exception:
            pass

    def _on_closed(self, sender, args):
        self._stop_live_polling()
        unit_name = self.cmb_unit.SelectedItem or ALL_UNITS[0]
        prec_idx = int(self.sld_precision.Value)
        save_config(self.project_guid, unit_name, prec_idx)
        _set_active_window(None)
        try:
            self.ext_event.Dispose()
        except Exception:
            pass

    # -----------------------------------------------------------------
    # Copy & Toast
    # -----------------------------------------------------------------
    def _do_copy(self):
        text = self.txt_output.Text
        if text:
            WinClipboard.SetText(text)
            self._show_toast(u"\u2713 Copied to clipboard")

    def _show_toast(self, message):
        self.txt_toast.Text = message
        fade_in = DoubleAnimation()
        fade_in.From = 0.0
        fade_in.To = 1.0
        fade_in.Duration = Duration(TimeSpan.FromMilliseconds(200))

        fade_out = DoubleAnimation()
        fade_out.From = 1.0
        fade_out.To = 0.0
        fade_out.Duration = Duration(TimeSpan.FromMilliseconds(400))
        fade_out.BeginTime = TimeSpan.FromMilliseconds(1200)
        fade_out.FillBehavior = FillBehavior.Stop

        def on_fade_out_complete(s, e):
            self.brd_toast.Opacity = 0

        fade_out.Completed += on_fade_out_complete
        self.brd_toast.BeginAnimation(
            self.brd_toast.OpacityProperty, fade_in
        )

        import System
        timer = System.Windows.Threading.DispatcherTimer()
        timer.Interval = TimeSpan.FromMilliseconds(1400)

        def start_fade_out(s, e):
            timer.Stop()
            self.brd_toast.BeginAnimation(
                self.brd_toast.OpacityProperty, fade_out
            )

        timer.Tick += start_fade_out
        timer.Start()

    # -----------------------------------------------------------------
    # Live Polling
    # -----------------------------------------------------------------
    def _start_live_polling(self):
        if self._live_timer is not None:
            return
        import System
        self._live_timer = System.Windows.Threading.DispatcherTimer()
        self._live_timer.Interval = TimeSpan.FromMilliseconds(800)
        self._live_timer.Tick += self._on_live_tick
        self._live_timer.Start()

    def _stop_live_polling(self):
        if self._live_timer is not None:
            self._live_timer.Stop()
            self._live_timer = None

    def _on_live_tick(self, sender, args):
        try:
            self.ext_event.Raise()
        except Exception:
            pass

    # -----------------------------------------------------------------
    # Display Updates
    # -----------------------------------------------------------------
    def _update_precision_label(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        precisions = get_precisions(unit_name)
        idx = int(self.sld_precision.Value)
        idx = max(0, min(idx, len(precisions) - 1))
        self.txt_precision.Text = precisions[idx][0]

    def _update_display(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        prec_idx = int(self.sld_precision.Value)
        total = self._get_filtered_total()
        formatted = format_volume(total, unit_name, prec_idx)
        self.txt_output.Text = formatted

    def _update_grid(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        prec_idx = int(self.sld_precision.Value)
        filtered = self._get_filtered_rows()
        for row in filtered:
            row.vol_str = format_volume(
                row.vol_cuft, unit_name, prec_idx
            )
        self.dgd_elements.ItemsSource = None
        from System.Collections.ObjectModel import ObservableCollection
        collection = ObservableCollection[object]()
        for row in filtered:
            collection.Add(row)
        self.dgd_elements.ItemsSource = collection

    def _update_status(self, selected_count, valid_count, skipped):
        if selected_count == 0:
            self.txt_status.Text = "No elements selected"
        elif valid_count == 0:
            self.txt_status.Text = (
                "{0} element(s) selected \u2014 none with a volume parameter"
                .format(selected_count)
            )
        else:
            parts = [
                "{0} of {1} element(s) measured".format(
                    valid_count, selected_count
                )
            ]
            if skipped > 0:
                parts.append("{0} skipped".format(skipped))
            cat_count = len(self._categories)
            if cat_count > 1:
                parts.append("{0} categories".format(cat_count))
            self.txt_status.Text = u" \u00B7 ".join(parts)

    def show(self):
        self.window.Show()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    existing = _get_active_window()
    if existing is not None:
        try:
            if existing.window.IsVisible:
                existing.window.Activate()
                existing.refresh_from_selection()
                return
        except Exception:
            pass

    handler = SelectionUpdateHandler()
    ext_event = ExternalEvent.Create(handler)

    dialog = QuickVolumeWindow(ext_event, handler)
    _set_active_window(dialog)
    dialog.show()


main()
