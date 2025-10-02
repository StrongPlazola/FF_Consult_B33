import customtkinter as ctk
from app.core.configManager import load_config, save_config

class ImageConfigWindow(ctk.CTkToplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)

        self.title("Image Configuration")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()

        self.on_close = on_close

        container = ctk.CTkFrame(self, corner_radius=10, fg_color="#f2f2f2")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # 📂 Cargar config desde JSON
        config = load_config()
        img_cfg = config.get("images", {})

        title = ctk.CTkLabel(container, text="Set Image Path", font=("Arial", 18, "bold"))
        title.pack(pady=(10,15))

        # Entrada con valor desde el JSON
        self.path_entry = ctk.CTkEntry(container, width=300)
        self.path_entry.insert(0, img_cfg.get("path", "C:/SpecTrace/images"))
        self.path_entry.pack(pady=10)

        save_btn = ctk.CTkButton(container,
                                 text="💾 Save Path",
                                 font=("Arial", 14, "bold"),
                                 fg_color="#0078D7",
                                 hover_color="#005A9E",
                                 command=self.save_config)
        save_btn.pack(pady=(20,10), fill="x", padx=40)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def save_config(self):
        # 📂 Guardar la ruta en el JSON
        config = load_config()
        config["images"] = {
            "path": self.path_entry.get()
        }
        save_config(config)
        print("✅ Image path saved:", config["images"])
        self.destroy()

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()