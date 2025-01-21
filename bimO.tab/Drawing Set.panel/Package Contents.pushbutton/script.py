import os
import csv
import sys
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from pyrevit import forms
from pyrevit import script
from pyrevit import revit

__author__ = 'Tay Othman, AIA'

# create a folder browser dialog to select the folder
folder_path = forms.pick_folder()

# create an empty list to store the file names
subfiles = []
# Check if the folder exists
if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    # prompt to include the files on the main folder in addition to the files on the subfolders
    
    include_main_folder = forms.ask_for_one_item(["Yes", "No"], default="Yes", prompt="Include the files on the main folder in addition to the files on the subfolders?", title="Include Main Folder", width=300, height=200)
    # if the user cancels the dialog
    if include_main_folder == None:
        # exit the program
        sys.exit()
    # if the user wants to include the files on the main folder
    if include_main_folder == True:
        # loop through the files in the folder
        for file in files:
            # if the file is a pdf file
            if file.endswith('.pdf'):
                # add the file to the subfiles list
                subfiles.append([file.split('-')[0], file.split('-')[1], ''])
            # if the file is a folder
            elif os.path.isdir(os.path.join(folder_path, file)):
                # loop through the files in the subfolder
                for subfile in os.listdir(os.path.join(folder_path, file)):
                    # if the file is a pdf file
                    if subfile.endswith('.pdf'):
                        # check if the subfile contains a hyphen before splitting it
                        if '-' in subfile:
                            # add the file to the subfiles list
                            subfiles.append([subfile.split('-')[0], subfile.split('-')[1], file])
                        else:
                            print("Warning: {0} does not contain a hyphen and will be skipped.".format(subfile))
    # if the user does not want to include the files on the main folder
    else:
        # loop through the files in subfolders only
        for file in files:
            # if the file is a folder
            if os.path.isdir(folder_path + "\\" + file):
                # loop through the files in the subfolder
                for subfile in os.listdir(folder_path + "\\" + file):
                    # if the file is a pdf file
                    if subfile.endswith('.pdf'):
                        #search for file extension and remove it from the file name look for the last 4 characters
                        if subfile[-4] == '.':
                            # remove the last 4 characters from the file name
                            subfile = subfile[:-4]

                        # check if the subfile contains a hyphen before splitting it
                        if '-' in subfile:
                            # add the file to the subfiles list
                            subfiles.append([subfile.split('-')[0], subfile.split('-')[1], file])
                        else:
                            print("Warning: {0} does not contain a hyphen and will be skipped.".format(subfile))
                   
# if the folder does not exist
else:
    print("The folder does not exist")
    # exit the program
    exit()


# confirm the file is not being used by another program
try:
    # open the file
    file = open(folder_path + "\\file_contents.csv", "wb")
    # close the file
    file.close()
# if the file is being used by another program
except IOError:
    # prompt the user to close the file
    forms.alert("Please close the file and try again.", title="File is Open", header="File is Open", exit=True)
# create a csv file to store the file contents save the file in the same folder as folder_path
with open(folder_path + "\\file_contents.csv", "wb") as file:

    # create a csv writer object
    writer = csv.writer(file)
    # write the header row
    writer.writerow(["SHEET NUMBER", "SHEET NAME", "SUBFOLDER"])
    # write the file contents
    for subfile in subfiles:
        writer.writerow(subfile)

#
# open the csv file
os.startfile(folder_path + "\\file_contents.csv")   
