import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')

import System.Windows.Forms as WinForms
import System.IO as IO

from pyrevit import revit, DB, forms, script, HOST_APP, UI


def QuickConvertDWGtoRVT():
    curDoc = __revit__.ActiveUIDocument.Document
    if isinstance(curDoc.ActiveView, ViewSchedule):
        TaskDialog.Show("Error", "Please change your current view to something other than a schedule.")
        return
    else:
        curLink = None
        showFormLS(curDoc)

def ConvertDWGtoRVT():
    curDoc = __revit__.ActiveUIDocument.Document
    if isinstance(curDoc.ActiveView, ViewSchedule):
        TaskDialog.Show("Error", "Please change your current view to something other than a schedule.")
        return
    else:
        curLink = None
        showFormLayers(curDoc)

def showFormLS(curDoc, selectedLS=0, selectedDWG="", convertType="detail"):
    curForm = frmConvertWithLS(curDoc, selectedLS, selectedDWG, convertType)
    curForm.ShowDialog()
    if curForm.DialogResult == WinForms.DialogResult.Cancel:
        return
    elif curForm.DialogResult == WinForms.DialogResult.Yes:
        curElemID = __revit__.ActiveUIDocument.Selection.PickObject(ObjectType.Element, "Select DWG file").ElementId
        curElem = curDoc.GetElement(curElemID)
        if isinstance(curElem, ImportInstance):
            curLink = curElem
            showFormLS(curDoc, curForm.getSelectedLS(), curLink.Category.Name, curForm.getConvertType())
        else:
            TaskDialog.Show("Error", "Select an imported or linked DWG file.")
    elif curForm.DialogResult == WinForms.DialogResult.OK:
        if curLink is not None:
            counter = 0
            if validateLineTypeByView(curDoc, convertType):
                counter = ConvertDWG(curDoc, curLink, "", curForm.getSelectedLSName(), curForm.getConvertType())
            if counter > 0:
                TaskDialog.Show("Complete", "Created " + str(counter) + " " + convertType + " lines.")
            else:
                TaskDialog.Show("Error", "Could not create " + convertType + " lines in the current view.")
        else:
            TaskDialog.Show("Alert", "Please select a DWG to convert.")
            showFormLS(curDoc, curForm.getSelectedLS(), curForm.getConvertType())

def showFormLayers(curDoc, selectedDWG="", layerList=None, convertType="detail"):
    counter = 0
    curForm = frmConvertWithLayers(curDoc, selectedDWG, layerList, convertType)
    curForm.ShowDialog()
    if curForm.DialogResult == WinForms.DialogResult.Cancel:
        return
    elif curForm.DialogResult == WinForms.DialogResult.Yes:
        curElemID = __revit__.ActiveUIDocument.Selection.PickObject(ObjectType.Element, "Select DWG file").ElementId
        curElem = curDoc.GetElement(curElemID)
        if isinstance(curElem, ImportInstance):
            curLink = curElem
            layerList = getDWGLayers(curDoc, curLink)
            showFormLayers(curDoc, curLink.Category.Name, layerList, curForm.getConvertType())
        else:
            TaskDialog.Show("Error", "Select an imported or linked DWG file.")
    elif curForm.DialogResult == WinForms.DialogResult.OK:
        if curLink is not None:
            layerLinetypeList = curForm.getLayerLinetypeList()
            if len(layerLinetypeList) > 0:
                if validateLineTypeByView(curDoc, curForm.getConvertType()):
                    counter = ConvertDWGByLayers(curDoc, curLink, layerLinetypeList, curForm.getConvertType())
                if counter > 0:
                    TaskDialog.Show("Complete", "Created " + str(counter) + " " + curForm.getConvertType() + " lines.")
                else:
                    TaskDialog.Show("Error", "Could not create " + curForm.getConvertType() + " lines in the current view.")
        else:
            TaskDialog.Show("Alert", "Please select a DWG to convert.")
            showFormLayers(curDoc, curForm.getConvertType())

def ConvertDWG(curDoc, curLink, importFilepath, curLinestyle, convertType):
    docType = "family" if curDoc.IsFamilyDocument else "project"
    counter = 0
    curGeomList = GetLinkedDWGCurves(curLink, curDoc)
    with Transaction(curDoc, "Convert lines") as curTrans:
        curTrans.Start()
        if len(curGeomList) != 0:
            for curGeom in curGeomList:
                if isinstance(curGeom, PolyLine):
                    ptsList = curGeom.GetCoordinates()
                    counter += createPolylines(curDoc, ptsList, curLinestyle, convertType, docType)
                else:
                    counter += createLine(curDoc, curGeom, curLinestyle, convertType, docType)
        curTrans.Commit()
    return counter

def ConvertDWGByLayers(curDoc, curLink, layerList, convertType):
    docType = "family" if curDoc.IsFamilyDocument else "project"
    counter = 0
    curGeomList = GetLinkedDWGCurves(curLink, curDoc)
    with Transaction(curDoc, "Convert DWG to RVT") as curTrans:
        curTrans.Start()
        if len(curGeomList) != 0:
            for curGeom in curGeomList:
                curLayerName = ""
                try:
                    curGraphicStyle = curDoc.GetElement(curGeom.GraphicsStyleId)
                    curLayerName = curGraphicStyle.GraphicsStyleCategory.Name
                except:
                    pass
                curLinestyle = ""
                for curRow in layerList:
                    if curRow[0] == curLayerName:
                        curLinestyle = curRow[1]
                        break
                if curLinestyle:
                    if isinstance(curGeom, PolyLine):
                        ptsList = curGeom.GetCoordinates()
                        counter += createPolylines(curDoc, ptsList, curLinestyle, convertType, docType)
                    else:
                        if curLinestyle == "<Room Separation>":
                            counter += createRoomLine(curDoc, curGeom)
                        else:
                            counter += createLine(curDoc, curGeom, curLinestyle, convertType, docType)
        curTrans.Commit()
    return counter

def createPolylines(curDoc, ptsList, curLinestyle, convertType, docType):
    counter = 0
    for i in range(len(ptsList) - 1):
        try:
            if docType == "project":
                if convertType == "detail":
                    newDetailLine = curDoc.Create.NewDetailCurve(curDoc.ActiveView, Line.CreateBound(ptsList[i], ptsList[i + 1]))
                elif convertType == "area":
                    newModelLine = curDoc.Create.NewAreaBoundaryLine(curDoc.ActiveView.SketchPlane, Line.CreateBound(ptsList[i], ptsList[i + 1]), curDoc.ActiveView)
                elif convertType == "room":
                    newCurveArray = CurveArray()
                    newCurveArray.Append(Line.CreateBound(ptsList[i], ptsList[i + 1]))
                    newModelLineArr = curDoc.Create.NewRoomBoundaryLines(curDoc.ActiveView.SketchPlane, newCurveArray, curDoc.ActiveView)
                elif convertType == "space":
                    newCurveArray = CurveArray()
                    newCurveArray.Append(Line.CreateBound(ptsList[i], ptsList[i + 1]))
                    newModelLineArr = curDoc.Create.NewSpaceBoundaryLines(curDoc.ActiveView.SketchPlane, newCurveArray, curDoc.ActiveView)
                else:
                    newModelLine = curDoc.Create.NewModelCurve(Line.CreateBound(ptsList[i], ptsList[i + 1]), curDoc.ActiveView.SketchPlane)
            else:
                if convertType == "detail":
                    newDetailLine = curDoc.FamilyCreate.NewDetailCurve(curDoc.ActiveView, Line.CreateBound(ptsList[i], ptsList[i + 1]))
                else:
                    newModelLine = curDoc.FamilyCreate.NewModelCurve(Line.CreateBound(ptsList[i], ptsList[i + 1]), curDoc.ActiveView.SketchPlane)
            if newModelLine:
                newModelLine.LineStyle = getLinestyleByName(curDoc, curLinestyle)
            elif newDetailLine:
                newDetailLine.LineStyle = getLinestyleByName(curDoc, curLinestyle)
            counter += 1
        except:
            pass
    return counter

def createLine(curDoc, curGeom, curLinestyle, convertType, docType):
    counter = 0
    try:
        if docType == "project":
            if convertType == "detail":
                newDetailLine = curDoc.Create.NewDetailCurve(curDoc.ActiveView, curGeom)
            elif convertType == "area":
                newModelLine = curDoc.Create.NewAreaBoundaryLine(curDoc.ActiveView.SketchPlane, curGeom, curDoc.ActiveView)
            elif convertType == "room":
                newCurveArray = CurveArray()
                newCurveArray.Append(curGeom)
                newModelLineArr = curDoc.Create.NewRoomBoundaryLines(curDoc.ActiveView.SketchPlane, newCurveArray, curDoc.ActiveView)
            elif convertType == "space":
                newCurveArray = CurveArray()
                newCurveArray.Append(curGeom)
                newModelLineArr = curDoc.Create.NewSpaceBoundaryLines(curDoc.ActiveView.SketchPlane, newCurveArray, curDoc.ActiveView)
            else:
                newModelLine = curDoc.Create.NewModelCurve(curGeom, curDoc.ActiveView.SketchPlane)
        else:
            if convertType == "detail":
                newDetailLine = curDoc.FamilyCreate.NewDetailCurve(curDoc.ActiveView, curGeom)
            else:
                newModelLine = curDoc.FamilyCreate.NewModelCurve(curGeom, curDoc.ActiveView.SketchPlane)
        if newModelLine:
            newModelLine.LineStyle = getLinestyleByName(curDoc, curLinestyle)
        elif newDetailLine:
            newDetailLine.LineStyle = getLinestyleByName(curDoc, curLinestyle)
        counter += 1
    except:
        pass
    return counter

def createRoomLine(curDoc, curGeom):
    counter = 0
    roomCurveArray = CurveArray()
    roomCurveArray.Append(curGeom)
    try:
        newRoomLines = curDoc.Create.NewRoomBoundaryLines(curDoc.ActiveView.SketchPlane, roomCurveArray, curDoc.ActiveView)
        counter += 1
    except:
        pass
    return counter

def GetLinkedDWGCurves(curLink, curDoc):
    curveList = []
    curOptions = Options()
    geoElement = curLink.Geometry(curOptions)
    for geoObject in geoElement:
        geoInstance = geoObject
        geoElem2 = geoInstance.GetInstanceGeometry()
        for curObj in geoElem2:
            curveList.append(curObj)
    return curveList

def GetDWGLayers(curDoc, curLink):
    layerList = []
    curOptions = Options()
    geoElement = curLink.Geometry(curOptions)
    for geoObject in geoElement:
        geoInstance = geoObject
        geoElem2 = geoInstance.GetInstanceGeometry()
        for curObj in geoElem2:
            try:
                curGraphicStyle = curDoc.GetElement(curObj.GraphicsStyleId)
                if curGraphicStyle.GraphicsStyleCategory.Name not in layerList:
                    layerList.append(curGraphicStyle.GraphicsStyleCategory.Name)
            except:
                pass
    layerList.sort()
    return layerList

def drawLine(curDoc, curSketchPlane, pt1, pt2):
    tmpLine = Line.CreateBound(pt1, pt2)
    curModelLine = curDoc.Create.NewModelCurve(tmpLine, curSketchPlane)
    return curModelLine

def getLineweightArray(filepath):
    lineCount = GetNumberOfLines(filepath)
    counter = 1
    lineweightList = []
    for i in range(5, lineCount):
        curStruct = importLWStruct(counter, int(ReadTXTLine(filepath, lineCount, i)))
        lineweightList.append(curStruct)
        counter += 1
    return lineweightList

def ReadTXTLine(filepath, totalLine, line2Read):
    if totalLine < line2Read:
        return "No Such Line"
    with open(filepath, 'r') as file:
        lines = file.readlines()
    return lines[line2Read]

def GetNumberOfLines(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    return len(lines)

def getRevitLinestyleFromACADColor(curDoc, lwArray, acadColor):
    revitLW = 1
    for curLW in lwArray:
        if curLW.acadLW == acadColor:
            revitLW = curLW.revitLW
    allLinestyles = getAllLinestyles(curDoc)
    for curCat in allLinestyles:
        if curCat.GetLineWeight(GraphicsStyleType.Projection) == revitLW and curCat.LineColor.Equals(Color(0, 0, 0)) and "<" not in curCat.Name:
            return curCat.Name
    newLinestyle = CreateNewLinestyle(curDoc, "Line LW " + str(revitLW), Color(0, 0, 0), revitLW)
    return newLinestyle.Name

def validateLineTypeByView(curDoc, convertType):
    if convertType == "area":
        if isinstance(curDoc.ActiveView, AreaPlan):
            return True
        else:
            return False
    if convertType in ["room", "space"]:
        if isinstance(curDoc.ActiveView, ViewPlan):
            return True
        else:
            return False
    return True
