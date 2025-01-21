# Import the required Revit API classes
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import os

__title__ = 'Get Length'
__author__  = 'Tay Othman, AIA'

# Define the function to convert decimal feet to feet and inches
def convert_feet(decimal_feet):
    # Convert decimal feet to whole feet and remaining inches
    decimal_feet = float(decimal_feet)
    whole_feet = int(decimal_feet)
    remaining_inches = (decimal_feet - whole_feet) * 12

    # Convert remaining inches to whole inches and fractional inches
    whole_inches = int(remaining_inches)
    fractional_inches = round((remaining_inches - whole_inches) * 64) / 64
    if fractional_inches == 0.984375:
        whole_inches += 1
        fractional_inches = 0

    # Format the output string
    if whole_inches == 0:
        formatted_length = "{0}'".format(whole_feet)
    elif fractional_inches == 0:
        formatted_length = "{0}'-{1}\"".format(whole_feet, whole_inches)
    else:
        formatted_length = "{0}'-{1}".format(whole_feet, whole_inches)
        if fractional_inches != 0:
            formatted_length += " {0}/64\"".format(int(fractional_inches * 64))

    # Return the formatted string
    return formatted_length

# Define the function to get the length of a curve
def get_curve_length(curve):
    # Get the length of the curve
    length = curve.Length
    # Convert the length to feet and inches
    formatted_length = convert_feet(length)
    # Return the formatted length
    return formatted_length

# Get the current Revit document
doc = __revit__.ActiveUIDocument.Document

# Get the selected elements
selection = __revit__.ActiveUIDocument.Selection.GetElementIds()

# Initialize the total length to zero
total_length = 0

#determine if the selection is a wall or a line
for element_id in selection:
    # Get the element from the element id
    element = doc.GetElement(element_id)
    # Check if the element is a wall
    if isinstance(element, Wall):
        # Get the wall's location curve
        curve = element.Location.Curve
        # Get the length of the curve
        length = curve.Length
        # Add the length to the total length
        total_length += length
    # Check if the element is a curve element

    elif isinstance(element, CurveElement):
        # Get the curve from the element
        curve = element.GeometryCurve
        # Get the length of the curve
        length = curve.Length
        # Add the length to the total length
        total_length += length

# Convert the total length to feet and inches
formatted_total_length = convert_feet(total_length)

# Create a Revit dialog box to display the total length
TaskDialog.Show("Total Length", formatted_total_length)


