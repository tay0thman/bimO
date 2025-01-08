#!python3
from pyrevit import revit, script, DB, forms, HOST_APP
import os
import datetime
import psutil

import GPUtil

doc = __revit__.ActiveUIDocument.Document

def GetFileName(doc):
    """
    Retrieves the file path of the given document.
    Args:
        doc: The document object from which to retrieve the file path.
    Returns:
        str: The file path of the document if available, otherwise an error message.
    """

    try:
        return doc.PathName
    except Exception as e:
        return str(e)
    
def GetRevitProjectName(doc):
    try:
        return os.path.basename(doc.PathName)
    except Exception as e:
        return str(e)
    
def GetRevitProjectPath(doc):
    try:
        return os.path.dirname(doc.PathName)
    except Exception as e:
        return str(e)
    
def GetRevitProjectSize(doc):
    try:
        return os.path.getsize(doc.PathName)
    except Exception as e:
        return str(e)
    
def GetRevitWarnings(doc):
    try:
        return doc.GetWarnings()
    except Exception as e:
        return str(e)
    
def GetRevitWarningsCount(doc):
    try:
        return len(doc.GetWarnings())
    except Exception as e:
        return str(e)
    
def GetCurrentPCusername():
    try:
        return os.getlogin()
    except Exception as e:
        return str(e)
    
def GetRevitVersion():
    try:
        return revit.get_host_app_version()
    except Exception as e:
        return str(e)
    
def GetRevitBuild():
    try:
        return revit.get_host_app_build()
    except Exception as e:
        return str(e)
    
def GetDateandTime():
    try:
        return datetime.datetime.now()
    except Exception as e:
        return str(e)
    
def GetPCName():
    try:
        return os.environ['COMPUTERNAME']
    except Exception as e:
        return str(e)
    
#Get Current CPU Usage
def GetCPUUsage():
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        return str(e)
    
def GetRAMUsage():
    try:
        return psutil.virtual_memory().percent
    except Exception as e:
        return str(e)
    
def GetDiskUsage():
    try:
        return psutil.disk_usage('/').percent
    except Exception as e:
        return str(e)
    
#get the currentGPU usage
def GetGPUUsage():
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            return gpu.load*100
    except Exception as e:
        return str(e)

def GetGPUMemory():
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            return gpu.memoryUtil*100
    except Exception as e:
        return str(e)

def GetGPUName():
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            return gpu.name
    except Exception as e:
        return str(e)

def collect_data():
    try:
        data = {
            'Date and Time': GetDateandTime(),
            'Revit Project Name': GetRevitProjectName(doc),
            'Revit Project Path': GetRevitProjectPath(doc),
            'Revit Project Size': GetRevitProjectSize(doc),
            'Revit Warnings Count': GetRevitWarningsCount(doc),
            'Current PC Username': GetCurrentPCusername(),
            'Revit Version': GetRevitVersion(),
            'Revit Build': GetRevitBuild(),
            'PC Name': GetPCName(),
            'CPU Usage': GetCPUUsage(),
            'RAM Usage': GetRAMUsage(),
            'Disk Usage': GetDiskUsage(),
            'GPU Usage': GetGPUUsage(),
            'GPU Memory': GetGPUMemory(),
            'GPU Name': GetGPUName()
        }
        return data
    except Exception as e:
        return str(e)
support_email = 'tothman@boulderassociates'

def SendEmail():
    try:
        forms.send_mail(subject='Support Request',
                        body=collect_data(),
                        to=support_email,
                        attachments=[script.get_log_file()]
                        )
    except Exception as e:
        return str(e)
    
def print_data():
    try:
        data = collect_data()
        print (data)
        # for key, value in data.items():
        #     print("{}: {}".format(key, value))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    print_data()
