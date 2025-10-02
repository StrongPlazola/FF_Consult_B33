# app/core/scanner_link.py
import socket
import threading
import time
from app.core.configManager import load_config

class ScannerLink:
    def __init__(self, update_ui_callback, on_fail_callback=None, on_data_callback=None):
        self.update_ui = update_ui_callback
        self.on_fail_callback = on_fail_callback
        self.on_data_callback = on_data_callback
        self.sock = None
        self.connected = False
        self.running = False

    def connect(self):
        """Intenta conectar al escáner y lanza el monitor de conexión"""
        config = load_config()
        scn_cfg = config.get("scanner", {})

        ip = scn_cfg.get("ip", "192.168.0.10")
        port = int(scn_cfg.get("port", 9004))

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.5)
            self.sock.connect((ip, port))
            self.connected = True
            self.update_ui(True)
            print(f"✅ Connected to Scanner {ip}:{port}")

            # Iniciar hilo para vigilar conexión
            self.running = True
            #threading.Thread(target=self._monitor, daemon=True).start()

        except Exception as e:
            print("❌ Scanner connection failed:", e)
            self.connected = False
            self.update_ui(False)
            if self.on_fail_callback:
                self.on_fail_callback()

    def _monitor(self):
        """Monitor que revisa si la conexión sigue viva"""
        try:
            while self.running and self.connected:
                try:
                    self.sock.sendall(b"\n")  # keep-alive
                except Exception as e:
                    print("⚠️ Scanner connection lost:", e)
                    self.connected = False
                    self.update_ui(False)
                    if self.on_fail_callback:
                        self.on_fail_callback()
                    break
                time.sleep(5)
        except Exception as e:
            print("⚠️ Error in scanner monitor:", e)

    def listen(self):
        """Escucha datos entrantes del escáner"""
        try:
            while self.connected:
                data = self.sock.recv(1024)
                if not data:
                    break
                print("📥 Data:", data.decode().strip())
        except Exception as e:
            print(f"⚠️ Scanner connection lost: {e}")
        finally:
            self.connected = False
            if self.update_ui:
                self.update_ui(False)
            if self.on_fail_callback:
                self.on_fail_callback()

    def send_trigger(self):
        """Envía trigger y espera respuesta rápida"""
        try:
            if self.connected and self.sock:
                self.sock.sendall(b"T2\r")
                print("📤 Trigger enviado al escáner (T2)")

                self.sock.settimeout(1.0)  # ⏱ 1 segundo máx
                try:
                    respuesta = self.sock.recv(1024).decode('utf-8').strip()
                    if respuesta:
                        print("📥 Respuesta recibida:", respuesta)
                        if self.on_data_callback:
                            self.on_data_callback(respuesta)
                except socket.timeout:
                    print("⚠️ No se recibió respuesta al trigger en el tiempo esperado")

            else:
                print("⚠️ No se pudo enviar trigger: no conectado")
        except Exception as e:
            print(f"❌ Error enviando trigger: {e}")
            self.connected = False
            if self.update_ui:
                self.update_ui(False)
            if self.on_fail_callback:
                self.on_fail_callback()

    def disconnect(self):
        """Cierra la conexión"""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.connected = False
        self.update_ui(False)