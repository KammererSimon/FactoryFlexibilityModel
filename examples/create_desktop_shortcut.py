# This file is not part of the factory flexibility model itself. It is just a standalone function to be executed directly from poetry to create a desktop shortcut for the tool GUI

# IMPORTS
import os

import win32com.client


# CODE START
def create_desktop_shortcut():
    """
    This function creates two files:
    1) A batch file "FactoryGUI.bat" within the factory_flexibility_model.ui-folder that starts the FactoryGUI as a standalone application on execution
    2) A shortcut on the Desktop that calls the batch-file
    """

    # get path to factory model root folder
    session_path = os.getcwd()

    # define content for batch file that calls the standalone gui
    batch_content = f"@echo off\n" f"cd {session_path}\n" f"poetry run gui"
    batch_path = f"{session_path}\\factory_flexibility_model\\ui\\FactoryGUI.bat"

    # create batch file
    with open(batch_path, "w") as batch_file:
        batch_file.write(batch_content)

    # get path to desktop
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop_path, "Factory Flexibility Model.lnk")

    # Create shortcut-object
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)

    # Configure Shortcut
    shortcut.Targetpath = batch_path
    shortcut.WorkingDirectory = os.path.dirname(batch_path)
    shortcut.IconLocation = (
        f"{session_path}\\factory_flexibility_model\\ui\\assets\\FM_shortcut.ico"
    )
    shortcut.WindowStyle = 7  # open shell in minimized mode
    shortcut.Description = "Factory Flexibility Model"
    shortcut.save()

    print("Desktop shortcut for standalone GUI execution successfully created!")
