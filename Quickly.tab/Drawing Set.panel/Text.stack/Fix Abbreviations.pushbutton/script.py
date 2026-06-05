# -*- coding: utf-8 -*-
# Author: Tay Othman
"""Find text notes containing dotted abbreviations like "U.O.N." and convert each match to "UON.".

A dotted abbreviation is any whitespace-separated token longer than 3 chars
that starts with an uppercase letter, has a period in position 2, and an
uppercase letter in position 3 (so "U.O.N.", "M.E.P.", "T.B.D.") all match.
"""
from pyrevit import revit, DB, forms, script

__title__ = "Fix\nAbbreviations"
__author__ = "Tay Othman, AIA"
__min_revit_ver__ = 2024
__max_revit_ver__ = 2027

doc = revit.doc


def _is_dotted_abbreviation(word):
    return len(word) > 3 and word[0].isupper() and word[1] == "." and word[2].isupper()


def _context_around(text, match_word):
    words = text.split()
    if match_word not in words:
        return text[:80] + ("…" if len(text) > 80 else "")
    i = words.index(match_word)
    return " ".join(words[max(0, i - 20):min(len(words), i + 20)])


class _TextNoteItem(forms.TemplateListItem):
    @property
    def name(self):
        note = doc.GetElement(self.item)
        text = note.Text or ""
        for w in text.split():
            if _is_dotted_abbreviation(w):
                return _context_around(text, w)
        return text


text_notes = list(DB.FilteredElementCollector(doc).OfClass(DB.TextNote))
matching_ids = [n.Id for n in text_notes
                if any(_is_dotted_abbreviation(w) for w in (n.Text or "").split())]

if not matching_ids:
    forms.alert("No text notes contain a dotted abbreviation.",
                title="Nothing To Fix",
                exitscript=True)

picked = forms.SelectFromList.show(
    [_TextNoteItem(nid) for nid in matching_ids],
    button_name="Fix Selected",
    multiselect=True,
)
if not picked:
    script.exit()

fixed_count = 0
with revit.Transaction("Fix Abbreviations"):
    for note_id in picked:
        note = doc.GetElement(note_id)
        words = (note.Text or "").split()
        changed = False
        for idx, word in enumerate(words):
            if _is_dotted_abbreviation(word):
                words[idx] = word.replace(".", "") + "."
                changed = True
        if changed:
            note.Text = " ".join(words)
            fixed_count += 1

forms.alert("Updated {} text note(s).".format(fixed_count),
            title="Fix Abbreviations")
