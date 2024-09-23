# -*- coding: utf-8 -*-

__title__ = 'Animation'
__doc__ = """
BETA!
    """

#######################################
# IMPORTS
#######################################
from re import X
import sys
import time
from math import sin

from Autodesk.Revit.DB import *  
from Autodesk.Revit.UI.Selection import *
# pyRevit

# .NET
import clr
clr.AddReference('System') 
from System.Collections.Generic import List
# List_example = List[ElementId]()

#######################################
# VARIABLES
#######################################
doc           = __revit__.ActiveUIDocument.Document     # type: Document
uidoc         = __revit__.ActiveUIDocument              # type: UIDocument
selection     = uidoc.Selection                         # type: Selection
#######################################
# MAIN
#######################################

def move_element_with_animation(doc, element_id, start_position, end_position, steps, delay_ms):
    # Start a transaction for the entire animation process
    t = Transaction(doc, "Animate Element Movement")
    

    # Calculate the incremental movement per step
    movement_step = (end_position - start_position) / steps

    # Start with the initial position
    current_position = start_position

    for i in range(steps + 1):
        t.Start()
        # Move the element incrementally
        ElementTransformUtils.MoveElement(doc, element_id, movement_step)

        # Wait/delay to simulate animation (convert ms to seconds)
        time.sleep(delay_ms / 1000.0)

        t.Commit()
        uidoc.RefreshActiveView()

element = selection
if not element:
    print('No element has been selected, exiting script')
    sys.exit()

element_id = selection.GetElementIds()[0]
element = doc.GetElement(element_id)
old_point = element.Location.Point
# XYZ defaults to (0,0,0)
new_point = XYZ(old_point.X + 10.0, (old_point.Y) + sin(old_point.X)*10 , old_point.Z)


move_element_with_animation(doc, element_id, old_point, new_point, 500, 10)
# ---------------------------------------------------------
print(50 * '-')
print('Script {{ {} }} has finished running'.format(__title__))