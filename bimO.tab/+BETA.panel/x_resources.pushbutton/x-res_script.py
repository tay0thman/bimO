from pyrevit import script, DB, forms, HOST_APP
doc = __revit__.ActiveUIDocument.Document
paths = []
def GetExtFileRefPath(item):
    try:
        dirRefs = item.GetExternalResourceReferences()
        for _, v in enumerate(dirRefs):
            return v.Value.InSessionPath
    except Exception as e:
        return str(e)
items = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType).ToElements()
for i in items:
    paths.append(GetExtFileRefPath(i))
    print(GetExtFileRefPath(i))
