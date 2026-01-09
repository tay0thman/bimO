#! python3
import sys
import os
import random
import ctypes

# --- PATCH: FIX SYS.PATH FOR COMPILED LOADER ---
try:
    import pyrevit
except ImportError:
    # 1. Find the path that contains the CPython Engine
    engine_path = next((p for p in sys.path if "pyRevit-Master" in p and "cengines" in p), None)
    
    if engine_path:
        # 2. Derive the root 'pyrevitlib' folder
        root_path = engine_path.split(r"\bin")[0]
        lib_path = os.path.join(root_path, "pyrevitlib")
        site_path = os.path.join(root_path, "site-packages")

        # 3. Inject into sys.path
        if os.path.exists(lib_path) and lib_path not in sys.path:
            sys.path.append(lib_path)
        if os.path.exists(site_path) and site_path not in sys.path:
            sys.path.append(site_path)

# Now we can safely import
try:
    from pyrevit import script
except ImportError:
    ctypes.windll.user32.MessageBoxW(0, "Still cannot find 'pyrevitlib'.", "Critical Error", 0)
    sys.exit()

# --- END PATCH ---

# Get the output window object
output = script.get_output()

# --- GRAPHICS CONFIGURATION ---
MATRIX_CHARS = ["0", "1", "ï", "ç", "§", "£", "¢", "¬", "µ", "¶"]
COLOR_CPYTHON = "#00FF41" # Matrix Green
COLOR_IRON = "#FF4500"    # Orange Red
COLOR_BG = "#0D0208"      # Dark background

def render_header(is_cpython):
    """Renders the status header."""
    version_info = sys.version.split(" ")[0]
    
    if is_cpython:
        status_text = "CPYTHON LOADER: ACTIVE"
        sub_text = "Kernel: v{} | Encoding: UTF-8".format(version_info)
        theme_color = COLOR_CPYTHON
        art = r"""
<pre style="font-family:monospace; line-height:10px; font-weight:bold;">
      _______   _______ 
     /  ____|  |  __   \ 
    |  |  __   | |__)  |
    |  | |_ |  |  ___ / 
    |  |__| |  | |      
     \______|  |_|      
</pre>
        """
    else:
        status_text = "IRONPYTHON DETECTED"
        sub_text = "Kernel: v{} | Standard pyRevit Engine".format(version_info)
        theme_color = COLOR_IRON
        art = r"""
<pre style="font-family:monospace; line-height:10px; font-weight:bold;">
      ______   ______ 
     |  ____| |  ____|
     | |__    | |__   
     |  __|   |  __|  
     | |      | |____ 
     |_|      |______|
</pre>
        """

    style = """
        background-color: {};
        color: {};
        padding: 20px;
        border: 2px solid {};
        border-radius: 10px;
        font-family: 'Consolas', monospace;
        text-align: center;
    """.format(COLOR_BG, theme_color, theme_color)

    html = """
    <div style="{style}">
        {art}
        <h1 style="margin:0;">{status}</h1>
        <p>{sub}</p>
    </div>
    """.format(style=style, art=art, status=status_text, sub=sub_text)

    # Safety check for print_html vs older methods
    if hasattr(output, 'print_html'):
        output.print_html(html)
    else:
        # Fallback for very raw wrappers
        print(status_text)
        print(sub_text)

def render_matrix_rain():
    """Generates a random stream of characters."""
    stream_html = "<div style='background-color:#000; padding:10px; font-family:monospace; overflow-x:hidden;'>"
    
    for i in range(10): 
        line = ""
        for j in range(40): 
            char = random.choice(MATRIX_CHARS)
            opacity = random.uniform(0.3, 1.0)
            size = random.randint(10, 16)
            line += "<span style='color:#008F11; opacity:{}; font-size:{}px'>{} </span>".format(opacity, size, char)
        stream_html += "<div style='line-height:12px'>{}</div>".format(line)
    
    stream_html += "</div>"
    
    if hasattr(output, 'print_html'):
        output.print_html(stream_html)

# --- MAIN EXECUTION ---

# REMOVED: output.wipe() cause attribute error in this environment

# Check Implementation
try:
    is_cpython = (sys.implementation.name.lower() == 'cpython')
except AttributeError:
    is_cpython = False

# Render
render_header(is_cpython)

if is_cpython:
    if hasattr(output, 'print_html'):
        output.print_html("<br><h3>Initializing Graphics Subsystem...</h3>")
        render_matrix_rain()
        output.print_html("<br><div style='color:#fff; background-color:green; padding:5px; text-align:center'>LOADER TEST PASSED</div>")
    else:
        print("LOADER TEST PASSED (HTML Output Not Supported)")
else:
    if hasattr(output, 'print_html'):
        output.print_html("<br><div style='color:#fff; background-color:red; padding:5px; text-align:center'>LOADER TEST FAILED (Running IronPython)</div>")
    else:
        print("LOADER TEST FAILED (Running IronPython)")