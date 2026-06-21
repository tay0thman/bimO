# -*- coding: utf-8 -*-
"""Shared engine for the Quick Measure tools (Area / Length / Volume).

Each tool is a thin script that builds a ``QuantitySpec`` describing its units,
precisions, value extraction and formatting, then calls :func:`launch`. All of
the modeless-WPF machinery, selection handling, live polling, category filters,
config persistence and unit detection lives here so it is written — and fixed —
once.
"""
import clr
import os
import math
import time

clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System")
clr.AddReference("System.Xml")

from System.Windows import Window, Visibility, Clipboard as WinClipboard, Duration
from System.Windows.Controls.Primitives import ToggleButton
from System.Windows.Markup import XamlReader
from System.Windows.Media.Animation import DoubleAnimation, FillBehavior
from System.IO import StringReader
from System.Xml import XmlReader as SysXmlReader
from System import TimeSpan

import xml.etree.ElementTree as ET

from Autodesk.Revit.DB import ElementId, BuiltInParameter
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent

from pyrevit import revit, DB, script

logger = script.get_logger()

LARGE_SELECTION_THRESHOLD = 500

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", ""), "pyRevit", "Quickly")


# =============================================================================
# QUANTITY SPEC
# =============================================================================
class QuantitySpec(object):
    """Everything that distinguishes one Quick Measure tool from another."""

    def __init__(self, name, noun, xaml_path, config_filename,
                 imperial_units, metric_units,
                 imperial_precisions, metric_precisions,
                 unit_suffixes, spec_type_id, forge_map, default_unit,
                 default_imperial_prec_idx, default_metric_prec_idx,
                 extract, formatter,
                 conversions=None, prec_display_multipliers=None):
        self.name = name                          # "Area" / "Length" / "Volume"
        self.noun = noun                          # "area" / "length" / "volume"
        self.xaml_path = xaml_path
        self.config_filename = config_filename
        self.imperial_units = list(imperial_units)
        self.metric_units = list(metric_units)
        self.imperial_precisions = imperial_precisions
        self.metric_precisions = metric_precisions
        self.unit_suffixes = unit_suffixes
        self.spec_type_id = spec_type_id
        self.forge_map = forge_map
        self.default_unit = default_unit
        self.default_imperial_prec_idx = default_imperial_prec_idx
        self.default_metric_prec_idx = default_metric_prec_idx
        self.extract = extract                    # callable(element) -> value | None
        self.formatter = formatter                # "decimal" | "length"
        self.conversions = conversions or {}
        self.prec_display_multipliers = prec_display_multipliers or {}

    @property
    def all_units(self):
        return self.imperial_units + self.metric_units

    def is_imperial(self, unit_name):
        return unit_name in self.imperial_units

    def precisions_for(self, unit_name):
        if self.is_imperial(unit_name):
            return self.imperial_precisions
        return self.metric_precisions

    def default_prec(self, unit_name):
        if self.is_imperial(unit_name):
            return self.default_imperial_prec_idx
        return self.default_metric_prec_idx

    def detect_unit(self):
        """Detect the project's display unit via the modern ForgeTypeId API."""
        try:
            units = revit.doc.GetUnits()
            fo = units.GetFormatOptions(self.spec_type_id)
            uid = fo.GetUnitTypeId()
            type_id_str = uid.TypeId if hasattr(uid, "TypeId") else str(uid)
            for key, val in self.forge_map.items():
                if key in type_id_str:
                    return val
        except Exception as ex:
            logger.debug("Quick {0}: unit detection failed — {1}".format(self.name, ex))
        return self.default_unit

    def format(self, total_internal, unit_name, precision_index):
        if self.formatter == "length":
            return _format_length(self, total_internal, unit_name, precision_index)
        return _format_decimal_quantity(self, total_internal, unit_name, precision_index)


# =============================================================================
# FORMATTING
# =============================================================================
def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def format_decimal(value, precision_in_display_unit, suffix):
    """Round ``value`` to the given precision and append the unit suffix."""
    if precision_in_display_unit <= 0:
        precision_in_display_unit = 0.001
    rounded = round(value / precision_in_display_unit) * precision_in_display_unit
    if precision_in_display_unit >= 1.0:
        decimal_places = 0
    else:
        decimal_places = max(0, int(math.ceil(-math.log10(precision_in_display_unit))))
        decimal_places = min(decimal_places, 8)
    fmt = "{{0:.{0}f}}{{1}}".format(decimal_places)
    return fmt.format(rounded, suffix)


def _format_decimal_quantity(spec, total_internal, unit_name, precision_index):
    precisions = spec.precisions_for(unit_name)
    idx = max(0, min(precision_index, len(precisions) - 1))
    raw = total_internal * spec.conversions.get(unit_name, 1.0)
    prec_display = precisions[idx][1] * spec.prec_display_multipliers.get(unit_name, 1.0)
    return format_decimal(raw, prec_display, spec.unit_suffixes.get(unit_name, ""))


def _format_fractional(total_feet, precision_inches):
    total_inches = abs(total_feet) * 12.0
    sign = "-" if total_feet < 0 else ""

    if precision_inches >= 12.0:
        rounded_feet = int(round(total_inches / 12.0))
        return "{0}{1}'-0\"".format(sign, rounded_feet)

    rounded = round(total_inches / precision_inches) * precision_inches
    whole_feet = int(rounded // 12)
    remaining = rounded - (whole_feet * 12)
    whole_inches = int(remaining)
    frac = remaining - whole_inches

    if whole_inches >= 12:
        whole_feet += 1
        whole_inches -= 12

    frac_str = ""
    if precision_inches < 1.0 and frac > 1e-9:
        denom = int(round(1.0 / precision_inches))
        numer = int(round(frac / precision_inches))
        g = _gcd(numer, denom)
        if g > 0:
            numer = numer // g
            denom = denom // g
        if numer > 0 and numer < denom:
            frac_str = " {0}/{1}".format(numer, denom)
        elif numer >= denom:
            whole_inches += 1
            frac_str = ""
            if whole_inches >= 12:
                whole_feet += 1
                whole_inches -= 12

    return "{0}{1}'-{2}{3}\"".format(sign, whole_feet, whole_inches, frac_str)


# Length conversions from internal feet to each display unit's raw magnitude.
_LENGTH_RAW = {
    "Fractional Feet and Inches": 1.0,
    "Decimal Feet": 1.0,
    "Decimal Inches": 12.0,
    "Meters": 0.3048,
    "Centimeters": 30.48,
    "Millimeters": 304.8,
}
# Divisor turning the precision value (inches for imperial, mm for metric) into
# the display unit's own scale.
_LENGTH_PREC_DIV = {
    "Decimal Feet": 12.0,
    "Decimal Inches": 1.0,
    "Meters": 1000.0,
    "Centimeters": 10.0,
    "Millimeters": 1.0,
}


def _format_length(spec, total_feet, unit_name, precision_index):
    precisions = spec.precisions_for(unit_name)
    idx = max(0, min(precision_index, len(precisions) - 1))
    prec_value = precisions[idx][1]

    if unit_name == "Fractional Feet and Inches":
        return _format_fractional(total_feet, prec_value)

    raw = total_feet * _LENGTH_RAW.get(unit_name, 1.0)
    prec_display = prec_value / _LENGTH_PREC_DIV.get(unit_name, 1.0)
    return format_decimal(raw, prec_display, spec.unit_suffixes.get(unit_name, ""))


# =============================================================================
# ELEMENT HELPERS
# =============================================================================
def get_element_id_int(el):
    """Element id as int — handles Revit 2024+ (.Value) and older (.IntegerValue)."""
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
                    pname = el_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME)
                    if pname and pname.HasValue:
                        type_name = pname.AsString()
                    else:
                        type_name = getattr(el_type, "Name", "")
                except Exception:
                    type_name = getattr(el_type, "Name", "")
                if family_name and type_name:
                    return "{0} : {1}".format(family_name, type_name)
                return family_name or type_name or u"—"
    except Exception:
        pass
    try:
        return element.Name or u"—"
    except Exception:
        return u"—"


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


class ElementRow(object):
    """Breakdown-grid row. Exposes Area/Length/Volume aliases so each tool's
    XAML column binding resolves without per-tool row classes."""

    def __init__(self, element_id, category, family_type, value):
        self.element_id = element_id
        self.category = category
        self.family_type = family_type
        self.value = value          # internal units (sq ft / ft / cu ft)
        self.value_str = ""

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
    def Area(self):
        return self.value_str

    @property
    def Length(self):
        return self.value_str

    @property
    def Volume(self):
        return self.value_str


def collect_element_data(spec, elements):
    """Build ElementRow list from a selection. Returns (rows, skipped_count)."""
    rows = []
    skipped = 0
    t0 = time.time()
    total = len(elements)

    for i, el in enumerate(elements):
        try:
            value = spec.extract(el)
        except Exception:
            value = None
        if value is None or value <= 0:
            skipped += 1
            continue
        rows.append(ElementRow(
            get_element_id_int(el),
            get_element_category_name(el),
            get_element_family_type(el),
            value,
        ))
        if total > LARGE_SELECTION_THRESHOLD and (i + 1) % 500 == 0:
            logger.debug("Quick {0}: processed {1}/{2} ({3:.1f}s)"
                         .format(spec.name, i + 1, total, time.time() - t0))

    if skipped:
        logger.debug("Quick {0}: skipped {1} element(s) with no valid {2}"
                     .format(spec.name, skipped, spec.noun))
    return rows, skipped


# =============================================================================
# CONFIG PERSISTENCE (per-project, with %APPDATA% fallback)
# =============================================================================
def _resolve_config_path(spec):
    tool_dir = os.path.dirname(spec.xaml_path)
    local_path = os.path.join(tool_dir, spec.config_filename)
    try:
        test_file = os.path.join(tool_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return local_path
    except Exception:
        pass
    try:
        if not os.path.exists(APPDATA_DIR):
            os.makedirs(APPDATA_DIR)
        return os.path.join(APPDATA_DIR, spec.config_filename)
    except Exception:
        return local_path


def load_config(spec, project_guid):
    config_path = _resolve_config_path(spec)
    try:
        if os.path.exists(config_path):
            root = ET.parse(config_path).getroot()
            projects_el = root.find("Projects")
            if projects_el is not None:
                for guid in (project_guid, "default"):
                    for proj in projects_el.findall("Project"):
                        if proj.get("guid") == guid:
                            unit = proj.find("SelectedUnit").text
                            prec = int(proj.find("PrecisionIndex").text)
                            if unit in spec.all_units:
                                return unit, prec
    except Exception as ex:
        logger.debug("Quick {0}: could not load config — {1}".format(spec.name, ex))
    return None, None


def save_config(spec, project_guid, unit_name, precision_index):
    config_path = _resolve_config_path(spec)
    try:
        if os.path.exists(config_path):
            try:
                tree = ET.parse(config_path)
                root = tree.getroot()
            except Exception:
                root = ET.Element("QuickMeasureConfig")
                tree = ET.ElementTree(root)
        else:
            root = ET.Element("QuickMeasureConfig")
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
        logger.warning("Quick {0}: could not save config — {1}".format(spec.name, ex))


# =============================================================================
# SINGLETON WINDOW TRACKING (per tool, keyed by spec name)
# =============================================================================
_active_windows = {}


def _get_active_window(name):
    return _active_windows.get(name)


def _set_active_window(name, win):
    if win is None:
        _active_windows.pop(name, None)
    else:
        _active_windows[name] = win


# =============================================================================
# EXTERNAL EVENT HANDLER (Live Mode)
# =============================================================================
class SelectionUpdateHandler(IExternalEventHandler):
    """Refreshes the window with the current selection on Revit's main thread."""

    def __init__(self, name):
        self.window = None
        self._name = name

    def Execute(self, uiapp):
        if self.window is None:
            return
        try:
            self.window.refresh_from_selection()
        except Exception as ex:
            logger.debug("Quick {0} live update error: {1}".format(self._name, ex))

    def GetName(self):
        return "Quickly{0}SelectionUpdate".format(self._name)


# =============================================================================
# WPF MODELESS WINDOW CONTROLLER
# =============================================================================
class QuickMeasureWindow(object):
    """Controller for a modeless Quick Measure WPF dialog, driven by a spec."""

    def __init__(self, spec, ext_event, ext_handler):
        self.spec = spec
        self.all_units = spec.all_units
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

    # ----- Initialization -----
    def _load_xaml(self):
        with open(self.spec.xaml_path, "r") as f:
            xaml_str = f.read()
        xml_reader = SysXmlReader.Create(StringReader(xaml_str))
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

        for unit in self.all_units:
            self.cmb_unit.Items.Add(unit)

        saved_unit, saved_prec = load_config(self.spec, self.project_guid)
        if saved_unit is None:
            saved_unit = self.spec.detect_unit()
            if saved_unit not in self.all_units:
                saved_unit = self.all_units[0]
        if saved_prec is None:
            saved_prec = self.spec.default_prec(saved_unit)

        self._updating = True
        self.cmb_unit.SelectedItem = saved_unit
        self._configure_slider(saved_unit, saved_prec)
        self._updating = False

    def _configure_slider(self, unit_name, prec_index=None):
        precisions = self.spec.precisions_for(unit_name)
        max_val = len(precisions) - 1
        self.sld_precision.Minimum = 0
        self.sld_precision.Maximum = max_val
        if prec_index is not None:
            idx = max(0, min(prec_index, max_val))
        else:
            idx = max(0, min(int(self.sld_precision.Value), max_val))
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

    # ----- Selection Refresh -----
    def refresh_from_selection(self):
        selection = revit.get_selection()
        elements = selection.elements if selection else []
        selected_count = len(elements)
        rows, skipped = collect_element_data(self.spec, elements)
        self._all_rows = rows
        self._build_categories()
        self._build_filter_chips()
        self._update_display()
        self._update_grid()
        self._update_status(selected_count, len(rows), skipped)

    def _build_categories(self):
        self._categories = {}
        for row in self._all_rows:
            self._categories.setdefault(row.category, []).append(row)
        self._active_categories = set(self._categories.keys())

    def _build_filter_chips(self):
        self.pnl_filters.Children.Clear()
        self._chip_buttons = {}
        if len(self._categories) < 2:
            self.brd_filters.Visibility = Visibility.Collapsed
            return
        self.brd_filters.Visibility = Visibility.Visible
        for cat in sorted(self._categories.keys()):
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
        return [r for r in self._all_rows if r.category in self._active_categories]

    def _get_filtered_total(self):
        return sum(r.value for r in self._get_filtered_rows())

    # ----- Event Handlers -----
    def _on_unit_changed(self, sender, args):
        if self._updating:
            return
        self._updating = True
        unit_name = self.cmb_unit.SelectedItem
        if unit_name:
            old_is_imp = True
            if args.RemovedItems.Count > 0:
                old_is_imp = self.spec.is_imperial(args.RemovedItems[0])
            new_is_imp = self.spec.is_imperial(unit_name)
            if old_is_imp != new_is_imp:
                self._configure_slider(unit_name, self.spec.default_prec(unit_name))
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
            self.tgl_breakdown.Content = u"▼ Hide Element Breakdown"
            self.brd_breakdown.Visibility = Visibility.Visible
        else:
            self.tgl_breakdown.Content = u"▶ Show Element Breakdown"
            self.brd_breakdown.Visibility = Visibility.Collapsed

    def _on_grid_selection(self, sender, args):
        try:
            selected_item = self.dgd_elements.SelectedItem
            if selected_item and hasattr(selected_item, "element_id"):
                try:
                    eid = ElementId(int(selected_item.element_id))
                except Exception:
                    eid = ElementId(selected_item.element_id)
                from System.Collections.Generic import List
                id_list = List[ElementId]()
                id_list.Add(eid)
                revit.uidoc.Selection.SetElementIds(id_list)
        except Exception:
            pass

    def _on_closed(self, sender, args):
        self._stop_live_polling()
        unit_name = self.cmb_unit.SelectedItem or self.all_units[0]
        prec_idx = int(self.sld_precision.Value)
        save_config(self.spec, self.project_guid, unit_name, prec_idx)
        _set_active_window(self.spec.name, None)
        try:
            self.ext_event.Dispose()
        except Exception:
            pass

    # ----- Copy & Toast -----
    def _do_copy(self):
        text = self.txt_output.Text
        if text:
            WinClipboard.SetText(text)
            self._show_toast(u"✓ Copied to clipboard")

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
        self.brd_toast.BeginAnimation(self.brd_toast.OpacityProperty, fade_in)

        import System
        timer = System.Windows.Threading.DispatcherTimer()
        timer.Interval = TimeSpan.FromMilliseconds(1400)

        def start_fade_out(s, e):
            timer.Stop()
            self.brd_toast.BeginAnimation(self.brd_toast.OpacityProperty, fade_out)
        timer.Tick += start_fade_out
        timer.Start()

    # ----- Live Polling -----
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

    # ----- Display Updates -----
    def _update_precision_label(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        precisions = self.spec.precisions_for(unit_name)
        idx = max(0, min(int(self.sld_precision.Value), len(precisions) - 1))
        self.txt_precision.Text = precisions[idx][0]

    def _update_display(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        prec_idx = int(self.sld_precision.Value)
        self.txt_output.Text = self.spec.format(self._get_filtered_total(), unit_name, prec_idx)

    def _update_grid(self):
        unit_name = self.cmb_unit.SelectedItem
        if not unit_name:
            return
        prec_idx = int(self.sld_precision.Value)
        filtered = self._get_filtered_rows()
        for row in filtered:
            row.value_str = self.spec.format(row.value, unit_name, prec_idx)
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
                u"{0} element(s) selected — none with a {1} parameter"
                .format(selected_count, self.spec.noun)
            )
        else:
            parts = ["{0} of {1} element(s) measured".format(valid_count, selected_count)]
            if skipped > 0:
                parts.append("{0} skipped".format(skipped))
            if len(self._categories) > 1:
                parts.append("{0} categories".format(len(self._categories)))
            self.txt_status.Text = u" · ".join(parts)

    # ----- Public -----
    def show(self):
        self.window.Show()


# =============================================================================
# ENTRY POINT
# =============================================================================
def launch(spec):
    """Show the tool's modeless window (singleton per tool)."""
    existing = _get_active_window(spec.name)
    if existing is not None:
        try:
            if existing.window.IsVisible:
                existing.window.Activate()
                existing.refresh_from_selection()
                return
        except Exception:
            pass

    handler = SelectionUpdateHandler(spec.name)
    ext_event = ExternalEvent.Create(handler)
    dialog = QuickMeasureWindow(spec, ext_event, handler)
    _set_active_window(spec.name, dialog)
    dialog.show()
