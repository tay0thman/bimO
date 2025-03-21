import clr
clr.AddReference('System.Management')
from System.Management import ManagementObjectSearcher


def convert_driver_date(date):
    """Converts the driver date to a readable format.
    Args:
        date (str): The driver date in the decimal format.
    Returns:
        str: The driver date in the format YYYY-MM-DD."""
    return date[:4] + "-" + date[4:6] + "-" + date[6:8]

def get_gpu_vram(searcher_gpu):
    """Gets the total VRAM of the GPU.
    Args:
        searcher_gpu (ManagementBaseObject): The GPU object.
    Returns:
        str: The total VRAM of the GPU."""
    vram = searcher_gpu['AdapterRAM']
    if vram is not None:
        try:
            if vram == 4293918720:
                return ("Total VRAM: {0} MB OR MORE".
                        format(vram // (1024 ** 2)))
            else:
                return ("Total VRAM: {0} MB".
            format(vram // (1024 ** 2)))
        except Exception as e:
            return("Error processing GPU {0}: {1}".
                    format(searcher_gpu['Name'], str(e)))
    else:
        return "VRAM information not available"

def get_gpu_info():
    """Gets the GPU information.
    Returns:
        list: The GPU information."""
    searcher = ManagementObjectSearcher('SELECT * FROM Win32_VideoController')
    gpu_info = []
    for item in searcher.Get():
        gpu_info.append(item['Name'])
        print(item['Name'])
        driver_version = item['DriverVersion']
        driver_date = item['DriverDate']
        print("Driver Version: {0}".format(driver_version))
        print("Driver Date: {0}".format(convert_driver_date(driver_date)))
        print(get_gpu_vram(item))
        print("=" * 50)
    return gpu_info

if __name__ == '__main__':
    get_gpu_info()