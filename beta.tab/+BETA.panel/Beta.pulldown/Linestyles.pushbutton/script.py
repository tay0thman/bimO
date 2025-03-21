import clr
# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Analysis import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
import Autodesk.Revit.UI.Selection as selection


uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
doc = uidoc.Document

# variables
#Query all line styles in the model.
linestyles = FilteredElementCollector(doc).OfClass(linestyles).ToElements()