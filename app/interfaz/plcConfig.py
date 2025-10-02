# app/interfaz/plc_config.py
import customtkinter as ctk
from app.core.configManager import load_config, save_config

class PLCConfigWindow(ctk.CTkToplevel):
    def __init__(self, master, on_close=None):
        super().__init__(master)

        self.title("⚙️ PLC Configuration")
        self.geometry("400x400")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.lift()
        self.configure(fg_color="white")

        self.on_close = on_close

        container = ctk.CTkFrame(self, corner_radius=10, fg_color="#f2f2f2")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        config = load_config()
        plc_cfg = config.get("plc", {})

        title = ctk.CTkLabel(container, text="PLC Configuration", font=("Arial", 18, "bold"))
        title.pack(pady=(10,15))

        self.ip_entry    = self._add_field(container, "PLC IP:",       plc_cfg.get("ip", "192.168.0.1"))
        self.rack_entry  = self._add_field(container, "Rack:",         plc_cfg.get("rack", 0))
        self.slot_entry  = self._add_field(container, "Slot:",         plc_cfg.get("slot", 0))
        self.write_entry = self._add_field(container, "Write Memory:", plc_cfg.get("write_memory", "M2.0"))
        self.read_entry  = self._add_field(container, "Read Memory:",  plc_cfg.get("read_memory", "M1.0"))

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
        config["plc"] = {
            "ip": self.ip_entry.get(),
            "rack": int(self.rack_entry.get()),
            "slot": int(self.slot_entry.get()),
            "write_memory": self.write_entry.get(),
            "read_memory": self.read_entry.get()
        }
        save_config(config)
        print("✅ PLC config saved:", config["plc"])
        self.destroy()

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.destroy()