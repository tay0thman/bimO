from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script
doc = __revit__.ActiveUIDocument.Document

#_________________Logging
# ping this folder to check if it is accessible
import os
import getpass
from datetime import datetime
import os
import sys

__author__ = "Tay Othman, AIA"

# Class to show Textnotes by Text Segment
class TextNoteText(forms.TemplateListItem):
    @property
    def name(self):
        txtnote = doc.GetElement(self.item).Text
        # find the index of the first word that matches the pattern
        for word in txtnote.split():
            if len(word) > 3 and word[0].isupper() and word[1] == '.' and word[2].isupper():
                index = txtnote.split().index(word)
                # return the 10 words before and after the matched word
                txtseg = ' '.join(txtnote.split()[index-20:index+20])
        return txtseg
  

# Begin the script
# get all text notes in the entire document
text_notes = DB.FilteredElementCollector(revit.doc).OfClass(DB.TextNote)
# remark  --------- text_notes = DB.FilteredElementCollector(revit.doc, revit.active_view.Id).OfClass(DB.TextNote)
abbTextnotes = []
abbTextIds = []
abbTextSegments = []
displayText = []
counter = 0
# loop through each text note and check if any individual word matches the "*.x.*" pattern where x is an uppercase letter while * is any number of characters
for text_note in text_notes:
    text = text_note.Text
    # check if any word in the text note matches the pattern 
    if any(len(word) > 3 and word[0].isupper() and word[1] == '.' and word[2].isupper() for word in text.split()):
        # append the text note to the list
        abbTextnotes.append(text_note)
        abbTextIds.append(text_note.Id)
        # split the text note into individual words
        # create a string variable "displayText" that will be displayed in the SelectFromList dialog, the display text will inclode the matched word and the 10 words around it
        for word in text.split():
            if len(word) > 3 and word[0].isupper() and word[1] == '.' and word[2].isupper():
                index = text.split().index(word)
                displayText.append(' '.join(text.split()[index-20:index+20]))
                break
        # append the display text to abbtextsegments
        abbTextSegments.append(displayText)
# Terminate the script if there are no text notes that match the pattern
if len(abbTextnotes) == 0:
    forms.alert('No text notes match the pattern', title='No text notes found')
    script.exit()
            
# select all text notes that match the pattern
# use the SelectFromList class to display a list of text notes and allow the user to select one or more    
selectionfilter = forms.SelectFromList.show([TextNoteText(abb) for abb in abbTextIds] , button_name='Select Text Notes', multiselect=True, button_exit_name='Done')
# Terminate the script if the selection is cancelled
if selectionfilter is None:
    script.exit()

# Create a transaction
with revit.Transaction('Remove Abbreviations'):
    # Loop through the selection filter and update the text notes
    for text_note in selectionfilter:
        # get the text of the text note
        text = doc.GetElement(text_note).Text
        # split the text note into individual words
        for word in text.split():
            # check if the word matches the pattern
            if len(word) > 3 and word[0].isupper() and word[1] == '.' and word[2].isupper():
                # get the index of the word in the list of words
                index = text.split().index(word)
                # Remove periods from the word
                word = word.replace('.', '')
                #append a single period to the word
                word = word + '.'
                # update text with the new word
                text = text.replace(text.split()[index], word)
                # update the text note
                doc.GetElement(text_note).Text = text
                # update the counter
                counter += 1
                # break out of the loop
                break
# End the transaction

# Display a message box to show the number of text notes that were updated
forms.alert('Updated {} text notes'.format(counter), title='Text Notes Updated', warn_icon=False)

  



