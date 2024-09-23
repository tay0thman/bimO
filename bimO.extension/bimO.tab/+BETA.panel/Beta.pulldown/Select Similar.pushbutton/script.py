#this script prompt the user to select a revit element then it will select all the elements that are similar to the selected element specific to the element type
#using pyrevit's built in SelectSimilar method
import Autodesk.Revit.DB as DB
import pyrevit
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
import Autodesk.Revit.UI.Selection



__title__ = 'Select Similar'
__author__ = 'Tay Othman'
doc = __revit__.ActiveUIDocument.Document

#___________________________________________________________________________________________________________________________________________________________________________________________________________
Categorytypelist = ["Model", "Annotation", "Analytical Model"]
category_type = forms.SelectFromList.show(Categorytypelist, button_name='Select Category Type', multiselect=False, height=600, width=300, title='Select Category Type', title_bar_color=(0, 120, 215))

# Query all categories in the document
categories = doc.Settings.Categories

# Get all the model catrgories
model_categories = [cat for cat in categories if cat.CategoryType == DB.CategoryType.Model]
# get all the annotation categories
annotation_categories = [cat for cat in categories if cat.CategoryType == DB.CategoryType.Annotation]
# get all the Analytical Model Categories
analytical_categories = [cat for cat in categories if cat.CategoryType == DB.CategoryType.AnalyticalModel]

target_categories = []

if category_type == "Model":
    target_categories = model_categories
elif category_type == "Annotation":
    target_categories = annotation_categories
elif category_type == "Analytical":
    target_categories = analytical_categories

#____________________________________________________________Dictionary_____________________________________________________________________________________
#list the name of the target categories
target_category_names = [cat.Name for cat in target_categories]
# build a dictionary of category names and category objects
category_dict = {cat.Name: cat for cat in target_categories}
# sort the dictionary by cat.Name
sorted_dict = sorted(category_dict.items(), key=lambda x: x[0])

CategoriesList = []
CategoriesName = []
for keys, values in sorted_dict:
    CategoriesList.append(values)
    CategoriesName.append(keys)

selected_category = forms.SelectFromList.show(CategoriesName, button_name='Select Category', multiselect=False, height=600, width=300, title='Select Category', title_bar_color=(0, 120, 215))


