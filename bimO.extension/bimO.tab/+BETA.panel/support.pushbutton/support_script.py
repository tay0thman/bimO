#!python3
# -*- coding: utf-8 -*-
import psutil
import platform
import datetime
import os
import subprocess
from pyrevit import HOST_APP, DB, revit

# Global Variables
doc = revit.doc
divider = "-" * 50
target_email = "tay@tayothman.com"

def create_mailto_link(email, subject, body):
    mailto_link = f"mailto:{email}?subject={subject}&body={body}"
    return mailto_link

def send_support_email():
    email_subject = "Test_Revit_Support_Request"
    email_body = build_email_body()
    email_body_lines = email_body.split('\n')
    formatted_body = "%0D%0A".join(email_body_lines)
    subprocess.run(['powershell', '-Command', f'Start-Process "mailto:{target_email}?subject={email_subject}&body={formatted_body}"'])

def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def get_system_info():
    try:
        system = platform.system()
        version = platform.version()
        release = platform.release()
        if system == "Windows":
            os_info = f"{system} {release} ({version})"
        else:
            os_info = f"{system} {release} ({version})"
        return os_info
    except Exception as e:
        return f"Error: {str(e)}"

def get_computer_name():
    try:
        computer_name = platform.node()
        return computer_name
    except Exception as e:
        return f"Error: {str(e)}"

def get_username():
    try:
        username = os.getlogin()
        return username
    except Exception as e:
        return f"Error: {str(e)}"

def get_cpu_cores():
    try:
        cpu_info = f"{psutil.cpu_count()} cores"
        return cpu_info
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_cpu_brand():
    try:
        cpu_info = f"{platform.processor()}"
        return cpu_info
    except Exception as e:
        return f"Error: {str(e)}"

def get_total_memory():
    try:
        memory = psutil.virtual_memory()
        total_memory = memory.total
        total_gigabytes = round(
                    total_memory / (1024 ** 3), 0)
        return total_gigabytes
    except Exception as e:
        return f"Error: {str(e)}"

def get_memory_usage():
    try:
        memory = psutil.virtual_memory()
        used_memory = memory.used
        used_gigabytes = round(
                    used_memory / (1024 ** 3), 0)
        return used_gigabytes
    except Exception as e:
        return f"Error: {str(e)}"

def get_gpu_info():
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, shell=True)
    return result.stdout

def get_revit_version():
    try:
        revit_version = HOST_APP.app.VersionNumber
        revit_build = HOST_APP.app.VersionBuild
        return str(revit_version) + " (Build " + str(revit_build) + ")"
    except Exception as e:
        return f"Error: {str(e)}"

def collect_system_info():
    system_info = {
        "Revit Version": get_revit_version(),
        "Operating System": get_system_info(),
        "Computer Name": get_computer_name(),
        "Username": get_username(),
        "CPU Brand": get_cpu_brand(),
        "CPU Cores": get_cpu_cores(),
        "Total Memory": f"{get_total_memory()} GB",
        "Memory Usage": f"{get_memory_usage()} GB",
        "GPU Info": get_gpu_info()
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
    email_body = f"""Support Request
===============================================================================    
((( Please provide a detailed description of the issue you are experiencing below )))


===============================================================================
Revit Document Information

Document Name: {document_info['Document Name']}

Document Path: {document_info['Document Path']}

Active View: {document_info['Active View']}

===============================================================================
System Information

Revit Version: {system_info['Revit Version']}

Operating System: {system_info['Operating System']}

Computer Name: {system_info['Computer Name']}

Username: {system_info['Username']}

CPU Brand: {system_info['CPU Brand']}

CPU Cores: {system_info['CPU Cores']}

Total Memory: {system_info['Total Memory']}

Memory Usage: {system_info['Memory Usage']}

GPU Info: {system_info['GPU Info']}
"""

if __name__ == "__main__":
    send_support_email()