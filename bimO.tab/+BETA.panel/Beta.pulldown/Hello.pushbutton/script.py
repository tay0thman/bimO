import re
import sys
import os
import os.path as op
import string
from collections import OrderedDict, namedtuple

from functools import wraps
import datetime
import webbrowser
import clr # pylint: disable=import-error
clr.AddReference('AdWindows')
import Autodesk.Internal.InfoCenter #pylint: disable=import-error
import Autodesk.Windows.ComponentManager #pylint: disable=import-error

def result_item_result_clicked(sender, e, debug=False):
    """Callback for a result item click event."""
    if debug:
        print("Result clicked")  # using print_md here will break the script
    pass



def show_balloon(header, text, tooltip='', group='', is_favourite=False, is_new=False, click_result=result_item_result_clicked):
    r"""Show ballon in the info center section.

    Args:
        header (str): Category section (Bold)
        text (str): Title section (Regular)
        tooltip (str): Tooltip
        group (str): Group
        is_favourite (bool): Add a blue star before header
        is_new (bool): Flag to new
        timestamp (str): Set timestamp
        click_result (def): Executed after a click event

    Examples:
        ```python
        from pyrevit import forms
import datetime
from pyrevit import forms
        date = '2019-01-01 00:00:00'
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        forms.show_balloon("my header", "Lorem ipsum", tooltip='tooltip',   group='group', is_favourite=True, is_new=True, timestamp = date, click_result = forms.result_item_result_clicked)
        ```
    """
    result_item = Autodesk.Internal.InfoCenter.ResultItem()
    result_item.Category = header
    result_item.Title = text
    result_item.TooltipText = tooltip
    result_item.Group = group
    result_item.IsFavorite = is_favourite
    result_item.IsNew = is_new
  

    result_item.ResultClicked += click_result
    balloon = Autodesk.Windows.ComponentManager.InfoCenterPaletteManager.ShowBalloon(
        result_item)
    return balloon

# Example usage
show_balloon('header', 'text', 'tooltip', 'group', True, True, result_item_result_clicked)