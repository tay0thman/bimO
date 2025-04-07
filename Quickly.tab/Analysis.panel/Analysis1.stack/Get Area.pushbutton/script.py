from pyrevit import script, DB, forms
from pyrevit.forms import alert

__title__ = 'Get Area'
__author__  = 'Tay Othman, AIA'

def get_area(element):
    # Get the area of the element
    area = element.LookupParameter('Area').AsDouble()
    # Return the area
    return area

def format_area(area):
    # Format the area as a string
    formatted_area = str(area) + ' sqft'
    # Return the formatted area
    return formatted_area

def get_total_area(selection):
    # Get the current Revit document
    doc = __revit__.ActiveUIDocument.Document
    # Initialize the total area to zero
    total_area = 0
    # Get the area of each selected element
    for element_id in selection:
        # Get the element from the element id
        element = doc.GetElement(element_id)
        # Get the area of the element
        area = get_area(element)
        # Add the area to the total area
        total_area += area
    # Return the total area
    formatted_total_area = format_area(total_area)
    return formatted_total_area

# Get the current Revit document
doc = __revit__.ActiveUIDocument.Document

# Get the selected elements
selection = __revit__.ActiveUIDocument.Selection.GetElementIds()
forms.alert(msg=get_total_area(selection), title='Total Area', exitscript=True)