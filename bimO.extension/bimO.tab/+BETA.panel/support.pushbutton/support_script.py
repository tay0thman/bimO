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
    email_subject = "Support Request"
    email_body = build_email_body()
    mailto_link = create_mailto_link(target_email, email_subject, email_body)
    os.system(f'start {mailto_link}')

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
    
    for key, value in system_info.items():
        print(f"{key}: {value}")
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
    
    for key, value in document_info.items():
        print(f"{key}: {value}")
    return document_info

def build_email_body():
    document_info = collect_document_info()
    system_info = collect_system_info()
    email_body = f"""
    <h1>Support Request</h1>
    <br>
    <br>
    <br>
    <h2>Document Information</h2>
    <p><strong>Document Name:</strong> {document_info['Document Name']}</p>
    <p><strong>Document Path:</strong> {document_info['Document Path']}</p>
    <p><strong>Active View:</strong> {document_info['Active View']}</p>
    <br>
    <h2>System Information</h2>
    <p><strong>Revit Version:</strong> {system_info['Revit Version']}</p>
    <p><strong>Operating System:</strong> {system_info['Operating System']}</p>
    <p><strong>Computer Name:</strong> {system_info['Computer Name']}</p>
    <p><strong>Username:</strong> {system_info['Username']}</p>
    <p><strong>CPU Brand:</strong> {system_info['CPU Brand']}</p>
    <p><strong>CPU Cores:</strong> {system_info['CPU Cores']}</p>
    <p><strong>Total Memory:</strong> {system_info['Total Memory']}</p>
    <p><strong>Memory Usage:</strong> {system_info['Memory Usage']}</p>
    <p><strong>GPU Info:</strong> {system_info['GPU Info']}</p>
    """
    return email_body
if __name__ == "__main__":
    send_support_email()