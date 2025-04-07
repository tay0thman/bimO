"""Searches for text notes that contain code years other than the current code year.this is important to detect and fix any outdated code years in the project.

Copyright (c) 2023 Tay Othman
https://www.tayothman.com
"""
#pylint: disable=import-error,invalid-name,broad-except,superfluous-parens
import clr

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import * #use ElementId
from pyrevit import revit, DB, HOST_APP
from pyrevit import forms
from pyrevit import script
from System.Collections.Generic import List
import sys
import os

from pyrevit import output
output = script.get_output()

__author__ = 'Tay Othman, AIA'

# Set the active Revit application and document
doc = __revit__.ActiveUIDocument.Document
# get all text notes in the entire document
text_notes = DB.FilteredElementCollector(revit.doc).OfClass(DB.TextNote)
# remark  --------- text_notes = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfClass(DB.TextNote)
abbTextnotes = []
abbTextIds = []
abbTextSegments = []

# display at dialogbox with dropdown for current code years 2007, 2010, 2013, 2016, 2019, 2022, 2025
from pyrevit import forms
# prompt user to select a code year
code_year = forms.CommandSwitchWindow.show(["2016", "2019", "2022", "2025", "2028", "2031"], message="Select a code year", title="Code Year", exit_name="Cancel")
# Test out if the code year is empty
if code_year == None:
    sys.exit()
# loop through the entire text notes to check for the patterns of the years from "2010" to "2025" also look for the pattern of words "CBC", "11B" and "ADA"
for text_note in text_notes:
    if any(word in text_note.Text for word in [str(year) for year in range(2007, 2031) if year != int(code_year)]):
        abbTextnotes.append(text_note)
        abbTextIds.append(text_note.Id)
        abbTextSegments.append(text_note.Text)

# make a iCollection of text notes

abbTextnotes_toIsolate = List[ElementId](i.Id for i in abbTextnotes)
print('Found {} text notes'.format(len(abbTextnotes)))

for text_note in abbTextnotes:
    text = text_note.Text
    for text_note in abbTextnotes:
            text = text_note.Text
            for word in [str(year) for year in range(2007, 2031) if year != int(code_year)]:
                if word in text:
                    index = text.index(word)
                    prefix = text[index-10:index]
                    suffix = text[index+len(word):index+len(word)+10]
                    output.print_md('{} text:\"{}\"'.format(output.linkify(text_note.Id), prefix + word + suffix))
