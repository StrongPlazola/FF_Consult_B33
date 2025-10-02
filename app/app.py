import customtkinter as ctk
from app.interfaz.mainWindow import mainWindow



def launchInterface():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # MAIN APP
    root = mainWindow()

    return root