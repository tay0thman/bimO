import clr

# Load the System.Management namespace
clr.AddReference("System.Management")
from System.Management import ManagementObjectSearcher

def get_dedicated_video_memory():
    searcher = ManagementObjectSearcher("SELECT DedicatedVideoMemory FROM Win32_VideoController")
    for item in searcher.Get():
        if item.Properties["DedicatedVideoMemory"].Value is not None:
            print("Dedicated Video Memory: {} bytes".format(item.Properties["DedicatedVideoMemory"].Value))
        else:
            print("Dedicated Video Memory: Not available")

if __name__ == "__main__":
    get_dedicated_video_memory()
