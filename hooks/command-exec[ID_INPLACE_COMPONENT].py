# pylint: skip-file
import os.path as op
from pyrevit import HOST_APP, EXEC_PARAMS
from pyrevit import revit, script, forms, DB, UI



args = EXEC_PARAMS.event_args



# Get the default view name.
print('Get the default view name.')
view_id = revit.doc.ActiveView.Id
view = revit.doc.GetElement(view_id)
view_name = view.Name
# prompt user for a view name
view_name_sting = forms.ask_for_string(
    prompt='Enter a name for the new 3D view',
    default=view_name,
    title='New 3D View Name',
    ok_text='Create')

# Rename the view
with revit.Transaction('Rename 3D View'):
    view.Name = view_name_sting
    

