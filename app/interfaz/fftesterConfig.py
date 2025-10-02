import customtkinter as ctk
from app.core.configManager import load_config, save_config

class FFTesterConfigWindow(ctk.CTkToplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)

        self.title("FFTester Configuration")
        self.geometry("600x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()
        self.configure(fg_color="white")

        self.on_close = on_close

        container = ctk.CTkFrame(self, corner_radius=10, fg_color="#f2f2f2")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        config = load_config()
        ff_cfg = config.get("fftester", {})

        title = ctk.CTkLabel(container, text="FFTester Configuration", font=("Arial", 18, "bold"))
        title.pack(pady=(10,15))

        # Campos de entrada
        self.wsdl_entry = self._add_field(container, "WSDL URL:", ff_cfg.get("wsdl", "http://127.0.0.1:9000/FFTester/?wsdl"))
        self.station_entry = self._add_field(container, "Station Name:", ff_cfg.get("station", "StationX"))
        self.user_entry = self._add_field(container, "User ID:", ff_cfg.get("user", "Admin"))

        save_btn = ctk.CTkButton(container,
                                 text="💾 Save Configuration",
                                 font=("Arial", 14, "bold"),
                                 fg_color="#0078D7",
                                 hover_color="#005A9E",
                                 command=self.save_config)
        save_btn.pack(pady=(20,10), fill="x", padx=40)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _add_field(self, parent, label_text, default_value):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)

        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w")
        label.pack(side="left", padx=5)

        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(default_value))
        entry.pack(side="right", fill="x", expand=True, padx=5)
        return entry

    def save_config(self):
        config = load_config()
        config["fftester"] = {
            "wsdl": self.wsdl_entry.get(),
            "station": self.station_entry.get(),
            "user": self.user_entry.get()
        }
        save_config(config)
        print("✅ FFTester config saved:", config["fftester"])
        self.destroy()

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()