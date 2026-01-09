#! python3
import sys
import random
from pyrevit import script

# Get the output window object
output = script.get_output()

# --- CONFIGURATION ---
MATRIX_CHARS = ["0", "1", "ï", "ç", "§", "£", "¢", "¬", "µ", "¶"]
# HTML Colors
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
        # Simple ASCII Art for Success
        art = """
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
        sub_text = "Kernel: v{} | This is not the CPython loader.".format(version_info)
        theme_color = COLOR_IRON
        art = """
<pre style="font-family:monospace; line-height:10px; font-weight:bold;">
      ______   ______ 
     |  ____| |  ____|
     | |__    | |__   
     |  __|   |  __|  
     | |      | |____ 
     |_|      |______|
</pre>
        """

    # CSS Styling for the box
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

    output.print_html(html)

def render_matrix_rain():
    """Generates a random stream of characters to test performance/encoding."""
    # We generate a block of HTML spans with varying opacities to simulate 'rain'
    stream_html = "<div style='background-color:#000; padding:10px; font-family:monospace; overflow-x:hidden;'>"
    
    for i in range(10): # Number of lines
        line = ""
        for j in range(40): # Width
            char = random.choice(MATRIX_CHARS)
            opacity = random.uniform(0.3, 1.0)
            size = random.randint(10, 16)
            line += "<span style='color:#008F11; opacity:{}; font-size:{}px'>{} </span>".format(opacity, size, char)
        stream_html += "<div style='line-height:12px'>{}</div>".format(line)
    
    stream_html += "</div>"
    output.print_html(stream_html)

# --- MAIN EXECUTION ---

# 1. Clear previous output
output.wipe()

# 2. Check Implementation
# 'cpython' vs 'ironpython'
try:
    # sys.implementation is available in Python 3 (CPython) and recent IronPython 3
    # standard IronPython 2.7 does not have sys.implementation
    impl_name = sys.implementation.name.lower()
except AttributeError:
    impl_name = "ironpython"

is_cpython_verified = (impl_name == 'cpython')

# 3. Render Output
render_header(is_cpython_verified)

if is_cpython_verified:
    output.print_html("<br><h3>Initializing Graphics Subsystem...</h3>")
    render_matrix_rain()
    output.print_html("<br><div style='color:#fff; background-color:green; padding:5px; text-align:center'>LOADER TEST PASSED</div>")
else:
    output.print_html("<br><div style='color:#fff; background-color:red; padding:5px; text-align:center'>LOADER TEST FAILED (Running IronPython)</div>")