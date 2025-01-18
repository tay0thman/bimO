import clr
clr.AddReference('System.Management')
from System.Management import ManagementObjectSearcher

def get_gpu_memory():
    searcher = ManagementObjectSearcher("SELECT AdapterRAM FROM Win32_VideoController")
    for obj in searcher.Get():
        memory_in_bytes = obj["AdapterRAM"]
        if "AdapterRAM" in obj.Properties:
            memory_in_bytes = obj["AdapterRAM"]
            memory_in_mb = memory_in_bytes / (1024 * 1024)  # Convert bytes to MB
            print("GPU Memory: {} MB".format(memory_in_mb))
        else:
            print("AdapterRAM property not found.")

get_gpu_memory()
