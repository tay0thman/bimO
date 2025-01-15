# -*- coding: utf-8 -*-
import platform
import datetime
import os
import System
import subprocess
import multiprocessing
from pyrevit import HOST_APP, DB, revit

import clr
clr.AddReference("System")
clr.AddReference("System.Management")
import System
from System.Diagnostics import Process
from System.Management import ManagementObjectSearcher

# Get CPU usage
def get_cpu_usage():
    cpu_usage = Process.GetCurrentProcess().TotalProcessorTime.TotalMilliseconds
    return cpu_usage

# Get RAM usage
def get_ram_usage():
    searcher = ManagementObjectSearcher("SELECT * FROM Win32_OperatingSystem")
    for os in searcher.Get():
        ram_usage = os["TotalVisibleMemorySize"]
    return ram_usage

print("CPU Usage:", get_cpu_usage())
print("RAM Usage:", get_ram_usage())

# Global Variables
doc = revit.doc
divider = "-" * 50
target_email = "tay@tayothman.com"

def create_mailto_link(email, subject, body):
    mailto_link = "mailto:" + email + "?subject=" + subject + "&body=" + body
    return mailto_link

def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def get_system_info():
    try:
        system = platform.system()
        version = platform.version()
        release = platform.release()
        if system == "Windows":
            os_info = "{} {} ({})".format(system, release, version)
        else:
            os_info = "{} {} ({})".format(system, release, version)
        return os_info
    except Exception as e:
        return "Error: {}".format(str(e))

def get_computer_name():
    try:
        computer_name = platform.node()
        return computer_name
    except Exception as e:
        return "Error: {}".format(str(e))

def get_username():
    try:
        username = os.environ.get('USERNAME')
        return username
    except Exception as e:
        return "Error: {}".format(str(e))

def get_cpu_cores():
    try:
        cpu_info = "{} cores".format(multiprocessing.cpu_count())
        return cpu_info
    except Exception as e:
        return "Error: {}".format(str(e))

def get_cpu_brand():
    try:
        cpu_info = System.Environment.GetEnvironmentVariable("PROCESSOR_IDENTIFIER")
        searcher = ManagementObjectSearcher("SELECT * FROM Win32_Processor")
        for item in searcher.Get():
            cpu_info = item["Name"]
        return cpu_info
    except Exception as e:
        return "Error: {}".format(str(e))

def get_project_info_number():
    try:
        project_number = doc.ProjectInformation.Number
        return project_number
    except Exception as e:
        return "Error: {}".format(str(e))

def get_total_memory():
    try:
        searcher = ManagementObjectSearcher("SELECT * FROM Win32_OperatingSystem")
        for os in searcher.Get():
            total_memory = int(os["TotalVisibleMemorySize"]) * 1024
        pass  # Removed undefined variable reference
        total_gigabytes = round(total_memory / (1024 ** 3), 0)
        return total_gigabytes
    except Exception as e:
        return "Error: {}".format(str(e))

def get_memory_usage():
    try:
        searcher = ManagementObjectSearcher("SELECT * FROM Win32_OperatingSystem")
        for os in searcher.Get():
            total_memory = int(os["TotalVisibleMemorySize"]) * 1024
            free_memory = int(os["FreePhysicalMemory"]) * 1024
        used_memory = total_memory - free_memory
        used_gigabytes = round(used_memory / (1024 ** 3), 0)
        return used_gigabytes
    except Exception as e:
        return "Error: {}".format(str(e))

def get_gpu_info():
    try:
        searcher = ManagementObjectSearcher("SELECT * FROM Win32_VideoController")
        gpu_info = []
        for item in searcher.Get():
            gpu_info.append(item["Name"])
        return ", ".join(gpu_info)
    except Exception as e:
        return "Error: {}".format(str(e))

def get_gpu_vram():
    try:
        searcher = ManagementObjectSearcher("SELECT * FROM Win32_VideoController")
        for item in searcher.Get():
            if item["AdapterRAM"] is not None:
                gpu_vram = round(int(float(item["AdapterRAM"])) / (1024 ** 3), 0)
            else:
                gpu_vram = "Unknown"
        return gpu_vram
    except Exception as e:
        return "Error: {}".format(str(e))

def get_revit_version():
    try:
        revit_version = HOST_APP.app.VersionNumber
        revit_build = HOST_APP.app.VersionBuild
        return "{} (Build {})".format(revit_version, revit_build)
    except Exception as e:
        return "Error: {}".format(str(e))

def collect_system_info():
    system_info = {
        "Revit Version": get_revit_version(),
        "Operating System": get_system_info(),
        "Computer Name": get_computer_name(),
        "Username": get_username(),
        "CPU Brand": get_cpu_brand(),
        "CPU Cores": get_cpu_cores(),
        "Total Memory": "{} GB".format(get_total_memory()),
        "Memory Usage": "{} GB".format(get_memory_usage()),
        "GPU Info": get_gpu_info(),
        "GPU VRAM": "{} GB".format(get_gpu_vram())
    }
    return system_info

def get_active_document_name():
    return doc.Title

def get_active_view():
    return doc.ActiveView.Name

def get_document_path():
    return doc.PathName

def collect_document_info():
    document_info = {
        "Document Name": get_active_document_name(),
        "Document Path": get_document_path(),
        "Active View": get_active_view()
    }
    return document_info

def build_email_body():
    document_info = collect_document_info()
    system_info = collect_system_info()
    email_body = """Support Request
===============================================================================    
((( Please provide a detailed description of the issue you are experiencing below )))


===============================================================================
Revit Document Information

Project Number: {}

Document Name: {}

Document Path: {}

Active View: {}

===============================================================================
System Information

Revit Version: {}

Operating System: {}

Computer Name: {}

Username: {}

CPU Brand: {}

CPU Cores: {}

Total Memory: {}

Memory Usage: {}

GPU Info: {}

GPU VRAM: {}
""".format(
        get_project_info_number(),
        document_info['Document Name'],
        document_info['Document Path'],
        document_info['Active View'],
        system_info['Revit Version'],
        system_info['Operating System'],
        system_info['Computer Name'],
        system_info['Username'],
        system_info['CPU Brand'],
        system_info['CPU Cores'],
        system_info['Total Memory'],
        system_info['Memory Usage'],
        system_info['GPU Info'],
        system_info['GPU VRAM']
    )
    return email_body

if __name__ == "__main__":
    email_subject = "Revit Support Request"
    email_body = build_email_body()
    mailto_link = create_mailto_link(target_email, email_subject, email_body)
    print(mailto_link)
    subprocess.Popen(mailto_link, shell=True)