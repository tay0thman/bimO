# -*- coding: utf-8 -*-
__title__   = "Pan Views"
__doc__     = """Version = 1.0
Date    = 10.17.2024
________________________________________________________________
Description:
Pan / Translate the view's crop box by a specified distance
________________________________________________________________
How-To:
1. Select a sheet
2. Select the views to pan
3. Enter the translation values
4. Enjoy the fun animations.
________________________________________________________________
TODO:
[FEATURE] - 1- Initial release
[KNOWN ISSUES] - 1- Some detail elements are not moving with the view
________________________________________________________________
Last Updates:
- [10.22.2024] v0.1 Initial Prototype
________________________________________________________________
Author: Tay Othman"""

#_______________________________________________________________________imports
from pyrevit import script, revit, DB, forms, HOST_APP

# Select a Sheet from the list
sheet = forms.select_sheets(title='Select Sheet',
                                button_name='Select Sheet',
                                multiple=False)

doc = revit.doc
# Get the list of views on the selected sheet
view_names = []
view_elements = []
views = sheet.GetAllPlacedViews()
if views == None:
    script.exit()
for view in views:
    view_element = doc.GetElement(view)
    view_elements.append(view_element)
    view_names.append(view_element.Name)

selected_view_names = forms.SelectFromList.show(view_names, 
                                            button_name='Select Views',
                                            multiselect=True)
if selected_view_names is None:
    script.exit()
selected_views = []

for view_name in selected_view_names:
    if view_name in view_names:
        view_obj = view_elements[view_names.index(view_name)]
        selected_views.append(view_obj)

# Get the translation values
x = forms.ask_for_number_slider( default=0, interval=1, min=-100, max=100,
                                 prompt='Enter the translation value in feet',
                                 title='X Translation')
y = forms.ask_for_number_slider( default=0, interval=1, min=-100, max=100,
                                prompt='Enter the translation value in feet',
                                title='Y Translation')
z = forms.ask_for_number_slider( default=0, interval=1, min=-100, max=100,
                                prompt='Enter the translation value in feet',
                                title='Z Translation')

with revit.Transaction('Move View Origin'):
    for view in selected_views:
                # Activate crop box
        view.CropBoxVisible = True
        filter = DB.ElementIsElementTypeFilter(True)
        dependent_ids = view.GetDependentElements(filter)
        print(dependent_ids[0])
        dependent = doc.GetElement(dependent_ids[0])
 
        # move the view element 4 feet up
        translate_vector = DB.XYZ(x, y, z)
        location_prop = dependent.Location.Move(translate_vector)
        print("Done")
        print("")
        # Deactivate crop box
        view.CropBoxVisible = False
        view.CropBoxActive = True


        # move filled regions

        # col1 = (DB.FilteredElementCollector(doc, view.Id)
        #                                         .OfClass(DB.FilledRegion)
        #                                         .WhereElementIsNotElementType()
        #                                         .ToElements())

        # for col in col1:
        #     try:
        #         col.Location.Move(translate_vector)
        #     except:
        #         print("Error moving filled region" + str(col.Id))
        #         pass
