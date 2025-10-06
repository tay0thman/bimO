from pyrevit import script, forms
from pyrevit import revit, DB
from pyrevit.interop import adc
import os


doc = revit.doc
doc_save_path = doc.PathName

def _get_organization_name(drv_info, path):
    """Get the organization name from the ADC path."""
    drive_schema = adc.ADC_DRIVE_SCHEMA.format(drive_name=drv_info.Name)
    parts = path.replace(drive_schema, "").split('/')
    file_name = parts[1]
    drv_local_path = os.path.normpath(drv_info.WorkspaceLocation)
    subdirs = os.walk(drv_local_path)
    for root, dirs, files in subdirs:
        for f in files:
            if f == file_name:
                file_path = os.path.join(root, f)
                org_name = file_path.replace(drv_local_path, "").split(os.sep)[1]
                return org_name
            

def get_model_path(path):
    """Get the Model Path of the model on ADC."""
    adc_obj = adc._get_adc()
    drv_info = adc._get_drive_from_path(adc_obj, path)
    org_name = _get_organization_name(drv_info, path)
    if org_name:
        if drv_info:
            drv_schema = adc.ADC_DRIVE_SCHEMA.format(drive_name=drv_info.Name)
            rel_path = path.replace(drv_schema, "")
            return os.path.normpath(os.path.join(
                drv_info.WorkspaceLocation,
                  org_name, 
                  rel_path
                )
            )
    return None

if not doc_save_path:
    script.exit()

try:
    adc_obj = adc._get_adc()    
except Exception as e:
    forms.alert("Could not access Autodesk Desktop Connector. Please ensure it is installed and running.",
                title="ADC Not Found", warn_icon=True)
    print(e)
    script.exit()
adc_save_path = get_model_path(doc_save_path)
adc_save_path_directory = os.path.join(
                os.path.dirname(adc_save_path),
                                "Project Files"
    )
if not os.path.exists(adc_save_path_directory):
    forms.alert("The local path for the current document does not exist.\n\n"
                "Local Path: {}".format(adc_save_path), title="Path Not Found",
                  warn_icon=True
    )
#navigate to the local path in file explorer
os.startfile(adc_save_path_directory)