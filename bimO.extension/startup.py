# this script is executed when the application starts up

from pyrevit import script
output = script.get_output()
output.add_style('body { font-family: Arial; font-size: 55px;  color: #33333;}')

output.print_html('<div style=body>Welcome to my BIM world</div>')


