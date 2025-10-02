# app/core/plc_link.py
import snap7
import threading
import time
from app.core.configManager import load_config
from snap7.type import Areas
from snap7.util import get_bool, set_bool

class PLCLink:
    def __init__(self, update_ui_callback, on_fail_callback=None):
        self.update_ui = update_ui_callback
        self.on_fail_callback = on_fail_callback
        self.client = snap7.client.Client()
        self.connected = False
        self.running = False

    def connect(self):
        config = load_config()
        plc_cfg = config.get("plc", {})

        ip = plc_cfg.get("ip", "192.168.0.1")
        rack = int(plc_cfg.get("rack", 0))
        slot = int(plc_cfg.get("slot", 0))

        try:
            self.client.connect(ip, rack, slot)
            if self.client.get_connected():
                print(f"✅ Connected to PLC {ip} (rack={rack}, slot={slot})")
                self.connected = True
                self.running = True
                self.update_ui(True)   # LED verde inicial
                threading.Thread(target=self._loop, daemon=True).start()
            else:
                self._fail()
        except Exception as e:
            print("❌ PLC connection failed:", e)
            self._fail()

    def _loop(self):
        config = load_config()
        plc_cfg = config.get("plc", {})

        write_mem = plc_cfg.get("write_memory", "M2")
        read_mem = plc_cfg.get("read_memory", "M1")

        try:
            heartbeat = True
            while self.running and self.client.get_connected():
                # --- Escribir heartbeat en M2 ---
                self._write_bit(write_mem, heartbeat)

                # --- Leer M1 ---
                state = self._read_bit(read_mem)

                print(f"🔄 Heartbeat={heartbeat} | {read_mem}={state}")

                # Actualizar LED según M1
                self.update_ui(state)

                heartbeat = not heartbeat
                time.sleep(3)   # ⏱ ahora cada 3 segundos
        except Exception as e:
            print("⚠️ Error in PLC loop:", e)
            self._fail()

    def _parse_memory(self, mem_str):
        """
        Convierte 'M1' en (Areas.MK, byte=0, bit=0)
        Convierte 'M2' en (Areas.MK, byte=0, bit=1)
        etc.
        """
        if mem_str.startswith("M"):
            idx = int(mem_str[1:]) - 1  # M1=0, M2=1, M3=2...
            byte = idx // 8
            bit = idx % 8
            return Areas.MK, byte, bit
        else:
            raise ValueError(f"Formato de memoria no soportado: {mem_str}")

    def _write_bit(self, mem_str, value):
        area, byte, bit = self._parse_memory(mem_str)
        data = self.client.read_area(area, 0, byte, 1)
        set_bool(data, 0, bit, value)
        self.client.write_area(area, 0, byte, data)

    def _read_bit(self, mem_str):
        area, byte, bit = self._parse_memory(mem_str)
        data = self.client.read_area(area, 0, byte, 1)
        return get_bool(data, 0, bit)

    def _fail(self):
        self.connected = False
        self.running = False
        self.update_ui(False)
        if self.on_fail_callback:
            self.on_fail_callback()

    def disconnect(self):
        self.running = False
        if self.client.get_connected():
            self.client.disconnect()
            print("🔌 PLC disconnected")
        self.connected = False
        self.update_ui(False)