# app/interfaz/
# menu_bar.py
import tkinter as tk
from app.interfaz.plcConfig import PLCConfigWindow
from app.interfaz.scannerConfig import ScannerConfigWindow
from app.interfaz.imageConfig import ImageConfigWindow

class menubar(tk.Menu):
    def __init__(self, master):
        super().__init__(master)

        # --- File ---
        m_file = tk.Menu(self, tearoff=0)
        m_file.add_command(label="New", command=lambda: print("New"))
        m_file.add_command(label="Open", command=lambda: print("Open"))
        m_file.add_separator()
        m_file.add_command(label="Leave", command=master.quit)
        self.add_cascade(label="File", menu=m_file)

        # --- Settings ---
        m_settings = tk.Menu(self, tearoff=0)
        m_settings.add_command(
            label="PLC Config",
            command=lambda: PLCConfigWindow(master)   # abre ventana de config
        )
        m_settings.add_command(
            label="Scanner Config",
            command=lambda: ScannerConfigWindow(master)
        )
        self.add_cascade(label="Settings", menu=m_settings)

        #Images
        image_menu = tk.Menu(self, tearoff=0)
        image_menu.add_command(label="Image Config", command=lambda: ImageConfigWindow(master))
        self.add_cascade(label="Images", menu=image_menu)



        # --- Help ---
        m_help = tk.Menu(self, tearoff=0)
        m_help.add_command(
            label="About",
            command=lambda: print("SpecTrace Program v1.0")
        )
        self.add_cascade(label="Help", menu=m_help)





