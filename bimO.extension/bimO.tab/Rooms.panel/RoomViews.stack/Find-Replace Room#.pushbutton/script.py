"""Rename Views by Room Number"""
#pylint: disable=import-error,invalid-name
from pydoc import doc
from pyrevit import forms, revit, DB, script

__title__ = 'Rename Views by Room'
__author__  = 'Tay Othman, AIA'

doc = revit.doc

oldroomparameter = "Room Numbers - Old"
newroomparameter = "Room Numbers - New"

# Define a function to collect all views in the document
def collect_views(doc):
    return DB.FilteredElementCollector(doc) \
           .OfCategory(DB.BuiltInCategory.OST_Views) \
           .WhereElementIsNotElementType() \
           .ToElements()

# Define a function to look for a three digit number in view names
def find_number(text):
    for word in text.split():
        if word.isdigit() and len(word) == 3:
            return word
    return
# Define a function to test a string for a three digit number between 000 and 999
def is_three_digit_number(text):
    for word in text.split():
        if word.isdigit() and 0 <= int(word) <= 999:
            return True
    return False
# Define a function to get all room numbers
def get_room_numbers():
    all_rooms = DB.FilteredElementCollector(doc).OfClass(DB.SpatialElement).ToElements()
    new_room_numbers = []
    for room in all_rooms:
        if room.Number:
            new_room_number = room.Number
            new_room_numbers.append(new_room_number)
    return new_room_numbers
# Define a function to get all old room numbers
def get_old_room_numbers():
    all_rooms = DB.FilteredElementCollector(doc).OfClass(DB.SpatialElement).ToElements()
    old_room_numbers = []
    for room in all_rooms:
        if room.LookupParameter(oldroomparameter):
            old_room_number = room.LookupParameter(oldroomparameter).AsString()
            old_room_numbers.append(old_room_number)
    return old_room_numbers

# define a function to look through all views names and titles on sheets
def rename_views_by_room():
    # current document views
    curdoc_views = collect_views(revit.doc)
    curdoc_views_dict = {revit.query.get_name(v): v for v in curdoc_views}
    # Get all rooms in the project
    all_rooms = DB.FilteredElementCollector(doc).OfClass(DB.SpatialElement).ToElements()
    # sort the rooms by number
    all_rooms = sorted(all_rooms, key=lambda x: x.Number)
    # Look for the values of revit.local.shared paramter "Room Numbers - Old" for each room
    old_room_numbers = get_old_room_numbers()
    # Look for the values of room.Number for each room
    new_room_numbers = get_room_numbers()
    #loop through all views and find names that contain a three digit number matches old room number
    all_views = collect_views(doc)
    for room in all_rooms:
        print('Processing room number: {}'.format(room.Number))
        if room.Number:
            for view in all_views:
                viewnameparam = view.Parameter[DB.BuiltInParameter.VIEW_NAME]
                viewname = revit.query.get_name(view)
                viewtitleparam = view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION]
                viewtitle = revit.query.get_param_value(viewtitleparam)
                # determine if there is a value in the viewtitle
                if viewtitle:
                    # if the viewtitle contains the old room number
                    if find_number(viewtitle) == room.LookupParameter(oldroomparameter).AsString():
                        # replace the old room number with the new room number
                        new_view_title = viewtitle.replace(find_number(viewtitle), room.Number)
                        # set the new view title
                        viewtitleparam.Set(new_view_title)
                        print('Renamed view: {} to {}'.format(viewtitle, new_view_title))
                else:
                    # if the viewname contains the old room number
                    if find_number(viewname):
                        if find_number(viewname) == room.LookupParameter(oldroomparameter).AsString():
                            # replace the old room number with the new room number
                            new_view_name = viewname.replace(find_number(viewname), room.Number)
                            # set the new view name
                            viewnameparam.Set(new_view_name)
                            print('Renamed view: {} to {}'.format(viewname, new_view_name))


                    

#call the function
if __name__ == '__main__':
    with revit.Transaction('Rename Views by Room'):
        rename_views_by_room()
    print('Views renamed successfully')

# rename_views_by_room()