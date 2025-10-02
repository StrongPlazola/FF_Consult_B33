import customtkinter as ctk
from app.core.configManager import load_config, save_config

class ScannerConfigWindow(ctk.CTkToplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)

        self.title("Scanner Configuration")
        self.geometry("400x250")
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
        sc_cfg = config.get("scanner", {})

        title = ctk.CTkLabel(container, text="Scanner Configuration", font=("Arial", 18, "bold"))
        title.pack(pady=(10,15))

        self.ip_entry   = self._add_field(container, "Scanner IP:", sc_cfg.get("ip", "192.168.0.50"))
        self.port_entry = self._add_field(container, "Port:", sc_cfg.get("port", 9004))

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
        config["scanner"] = {
            "ip": self.ip_entry.get(),
            "port": int(self.port_entry.get())
        }
        save_config(config)
        print("✅ Scanner config saved:", config["scanner"])
        self.destroy()

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()

