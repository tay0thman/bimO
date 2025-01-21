# Load the Python Standard and DesignScript Libraries

from os import name
from unicodedata import category
import clr

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Analysis import *
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
import Autodesk.Revit.UI.Selection as selection
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import System
from System.Collections.Generic import *

uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
doc = uidoc.Document
document = DB.Document

# Get the Revit version of the current UI document
version = doc.Application.VersionNumber
print(version)




