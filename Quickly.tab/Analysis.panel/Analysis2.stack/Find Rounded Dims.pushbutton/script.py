from pyrevit import script
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import HOST_APP
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import output 
import sys
import os
output = script.get_output()

__title__ = 'Find Rounded Dims'
__author__  = 'Tay Othman, AIA'
# define a function to convert a decimal number to a feet and fractional inches string rounded to the nearest Tolerance Level
def dec_to_feet(dec, tol_in):
    # Seperate Whole Feet from the Decimal
    Whole_feet = int(dec)
    # Get the Whole Number of inches
    inches = int((dec - Whole_feet) * 12)
    # Get the Fractional Inches
    frac = int(round(((dec - Whole_feet) * 12 - inches) * tol_in))
    if frac == tol_in:
        inches += 1
        frac = 0
    if inches == 12:
        Whole_feet += 1
        inches = 0
    feet = Whole_feet
    # Return the Feet and Fractional Inches as a String
    if frac == 0:
        if feet == 0:
            # Return Fractional Inches only
            return str(inches) +'"'
        else:
            # Return Whole Feet and Inches
            return str(feet) + "'-" + str(inches) + '"'
    else:
        # shrink the values to the lowest common denominator
        if frac % 2 == 0:
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        if frac % 2 == 0:
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        if frac % 2 == 0:
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        if frac % 2 == 0:  
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        if frac % 2 == 0:
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        if frac % 2 == 0:
            frac = int(frac / 2)
            tol_in = int(tol_in / 2)
        # Convert the Fractional Inches to a String
        frac_txt = str(frac) + str("/" + str(tol_in))
        # if the value of feet = 0, then return the fractional inches only
        if feet == 0:
            return str(inches) + " " + str(frac_txt) + '"'
        else:
            return str(feet) + "'-" + str(inches) + " " + str(frac_txt) + '"'
   

# prompt the user to select a tolerance level
tol = forms.CommandSwitchWindow.show(["1/16", "1/32", "1/64", "1/128", "1/256"], message="Select Tolerance Level", title="Tolerance Level", exit_on_close=True)
if tol == "1/16":
    tol = 16
elif tol == "1/32":
    tol = 32
elif tol == "1/64":
    tol = 64
elif tol == "1/128":
    tol = 128
elif tol == "1/256":
    tol = 256

# define output styles
output.add_style('overriden {background-color: #ff0000; color: #ffffff; font-weight: bold;}')
output.add_style('truevalue {background-color: #1e90ff; color: #ffffff; font-weight: bold;}')

# Collect All the Dimensions in the Document
doc = __revit__.ActiveUIDocument.Document
collector = FilteredElementCollector(doc)
collector.OfCategory(BuiltInCategory.OST_Dimensions)
collector.OfClass(Dimension)
dimCollector = collector.ToElements()

filtered_dimCollector = []

# Find and exlude the dimensions that has overridden values
for dim in dimCollector:
    if dim.ValueOverride == None:
        filtered_dimCollector.append(dim)

# Get the value string of each dimension
lin_dimVals = []
lin_dimValsRounded = []
lin_dimList = []
dshape = []
counter = 0
for dim in filtered_dimCollector:
    dshape = dim.DimensionShape
    if  dshape == DimensionShape.Linear or dshape == DimensionShape.Radial or dshape == DimensionShape.Diameter or dshape == DimensionShape.ArcLength:
        lin_dimVals.append(dim.Value)
        lin_dimValsRounded.append(dim.ValueString)
        #compare the value string to the value and if they are not equal, add the dimension to a list
        if dim.ValueString:
            # If dim.valuestring is starts with 0' - then remove it
            
            if str(dim.ValueString).startswith("0'-"):
                ValueString= str(dim.ValueString[4:])
            else:
                ValueString= str(dim.ValueString)
              
            if ValueString != str(dec_to_feet(dim.Value, tol)):
             counter += 1
             # lin_dimList.append(dim)
             # print the value string and the value
             # output with linkfy to the element
             truval = ValueString
             # rndval = str(dec_to_feet(dim.Value, tol))
             rndval = dec_to_feet(dim.Value, tol)
             seperator = '   >>>>>>>>>>>>>>>>>>>    '
             output.print_html('<truevalue>{}</truevalue>{}<overriden>{}</overriden>{}'.format(truval, seperator, rndval, output.linkify(dim.Id)))


print ("Total count of rounded dimensions: " + str(counter) + " out of " + str(len(lin_dimVals)) + " dimensions")
