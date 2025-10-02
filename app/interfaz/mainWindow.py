import customtkinter as ctk
import glob
from CTkMessagebox import CTkMessagebox
from tkinter import ttk   # para la tabla tipo Treeview
from PIL import Image
from zeep import Client
from customtkinter import CTkImage
from app.core.configManager import load_config
from app.interfaz.menuBar import menubar
from app.core.plcLink import PLCLink
from app.core.scannerLink import ScannerLink
from app.interfaz.plcConfig import PLCConfigWindow
from app.interfaz.scannerConfig import ScannerConfigWindow
import os
import time
import threading


class mainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        menu = menubar(self)
        self.config(menu=menu)
        # Configuración ventana
        self.title("SpecTrace Program Automation Philo @yp")
        self.update_idletasks()
        self.after(0, lambda: self.state("zoomed"))
        self.minsize(1200, 700)

        # Layout principal (grid con 2 columnas)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=2)   # Lado izquierdo grande
        self.grid_columnconfigure(1, weight=1)   # Panel derecho




        self.scanner_link = None
        self.scanner_attempted = False

        # --- FFTester config / client ---
        cfg = load_config()
        tcfg = cfg.get("fftester", {})
        self.ff_wsdl = tcfg.get("wsdl", "http://10.106.237.111:9000/FFTester/?wsdl")
        self.ff_station = tcfg.get("station", "BSLT-NESTS009")
        self.ff_user = tcfg.get("user", "Admin")
        self.ff_client = None  # se crea lazily en el thread cuando se use



        # ================= Header =================
        header = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="lightgray")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        header.grid_propagate(False)
        header.configure(height=50)

        tittle = ctk.CTkLabel(header, text="SpecTrace Program", font=("Arial", 18), text_color="white")
        tittle.pack(side="left", padx=20, pady=10)

        # ---- Status ----
        self.status_label = ctk.CTkLabel(header, text="Waiting for Testing...", font=("Arial", 40, "bold"))
        self.status_label.pack(side="right", padx=20, pady=10)

        # ================= LADO IZQUIERDO =================
        left_frame = ctk.CTkFrame(self, fg_color="white")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(0, weight=3)   # parte superior
        left_frame.grid_rowconfigure(1, weight=1)   # parte inferior
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_propagate(False)
        left_frame.configure(height=500, width=800)

        # ---- Área superior (dos paneles vacíos) ----
        top_area = ctk.CTkFrame(left_frame, fg_color="white")
        top_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        top_area.grid_columnconfigure((0,1), weight=1)
        top_area.grid_rowconfigure(0, weight=1)



        # ---- Área superior (dos paneles para cámaras) ----
        top_area = ctk.CTkFrame(left_frame, fg_color="white")
        top_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #
        top_area.grid_columnconfigure((0, 1), weight=1)  # ambas columnas ocupan espacio igual
        top_area.grid_rowconfigure(0, weight=1)



        # Frame de la cámara 1
        self.cam1_frame = ctk.CTkFrame(top_area, fg_color="#f2f2f2", border_width=1)
        self.cam1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #self.cam1_frame.grid_propagate(False)  # 👈 mantiene el tamaño aunque el label cambie

        self.cam1_label = ctk.CTkLabel(self.cam1_frame, text="Camera 1")
        self.cam1_label.pack(expand=True, fill="both")

        # Frame de la cámara 2
        self.cam2_frame = ctk.CTkFrame(top_area, fg_color="#f2f2f2", border_width=1)
        self.cam2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        #self.cam2_frame.grid_propagate(False)

        self.cam2_label = ctk.CTkLabel(self.cam2_frame, text="Camera 2")
        self.cam2_label.pack(expand=True, fill="both")


        # ---- Área inferior (Trigger Information) ----
        bottom_area = ctk.CTkFrame(left_frame, fg_color="white")
        bottom_area.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        bottom_area.grid_columnconfigure(0, weight=1)
        bottom_area.grid_rowconfigure(0, weight=1)

        # Trigger Information (tabla)
        trigger_frame = ctk.CTkFrame(bottom_area, fg_color="#e6e6e6", corner_radius=5)
        trigger_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=1)

        trigger_label = ctk.CTkLabel(trigger_frame, text="Trigger Information", font=("Arial", 14, "bold"))
        trigger_label.pack(anchor="w", padx=10, pady=5)

        # Tabla con Treeview
        columns = ("Message", "Count", "Result", "CameraPos1", "CameraRes1", "NumericRes1", "CameraPos2", "CameraRes2", "NumericRes2")
        self.table = ttk.Treeview(trigger_frame, columns=columns, show="headings", height=5)


        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, anchor="center")

        self.table.pack(fill="both", expand=True, padx=10, pady=5)

        # ================= PANEL DERECHO =================
        right_frame = ctk.CTkFrame(self, fg_color="lightgray")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure((0,1,2,3,4), weight=0)
        right_frame.grid_columnconfigure(0, weight=1)



        # ---- Model Selection ----
        model_section = ctk.CTkFrame(right_frame, fg_color="#e6e6e6", corner_radius=8, height=50)
        model_section.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        model_section.grid_columnconfigure(0, weight=1)
        model_section.grid_columnconfigure(1, weight=1)

        model_label = ctk.CTkLabel(model_section, text="Model Selection")
        model_label.grid(row=0, column=0, sticky="w", padx=10, pady=5, columnspan=2)

        model_combo = ctk.CTkOptionMenu(model_section, values=["VNext"])
        model_combo.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        pass_label = ctk.CTkLabel(model_section, text="Pass", width=120)
        pass_label.grid(row=1, column=1, sticky="w", padx=5)

        self.pass_entry = ctk.CTkEntry(model_section, width=80, justify="center")
        self.pass_entry.insert(0, "5")
        self.pass_entry.grid(row=1, column=1, sticky="e", padx=10)

        total_label = ctk.CTkLabel(model_section, text="Total", width=120)
        total_label.grid(row=2, column=1, sticky="w", padx=5)

        self.total_entry = ctk.CTkEntry(model_section, width=80, justify="center")
        self.total_entry.insert(0, "11")
        self.total_entry.grid(row=2, column=1, sticky="e", padx=10)

        yield_label = ctk.CTkLabel(model_section, text="Yield", width=120)
        yield_label.grid(row=3, column=1, sticky="w", padx=5)

        self.yield_entry = ctk.CTkEntry(model_section, width=80, justify="center")
        self.yield_entry.insert(0, "%45")
        self.yield_entry.grid(row=3, column=1, sticky="e", padx=10)

        config = load_config()
        counters = config.get("counters", {"pass": 0, "total": 0, "yield": 0})

        # limpiar antes de insertar
        self.pass_entry.delete(0, "end")
        self.pass_entry.insert(0, str(counters.get("pass", 0)))

        self.total_entry.delete(0, "end")
        self.total_entry.insert(0, str(counters.get("total", 0)))

        self.yield_entry.delete(0, "end")
        self.yield_entry.insert(0, f"%{counters.get('yield', 0)}")

        # ---- Product SN ----
        product_section = ctk.CTkFrame(right_frame, fg_color="#e6e6e6", corner_radius=8)
        product_section.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        product_section.grid_columnconfigure(0, weight=1)   #Product
        product_section.grid_columnconfigure(1, weight=1)   #Camera Link
        product_section.grid_columnconfigure(0, weight=1)

        sn_label = ctk.CTkLabel(product_section, text="Product SN:")
        sn_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        camera_label = ctk.CTkLabel(product_section, text="Camera")
        camera_label.grid(row=0, column=1, sticky="n", padx=10, pady=5)

        plc_label = ctk.CTkLabel(product_section, text="PLC Link")
        plc_label.grid(row=0, column=2, sticky="n", padx=10, pady=5)

        #Entrada de datos
        self.sn_entry = ctk.CTkEntry(product_section, placeholder_text="Enter Serial Number", state="normal")
        self.sn_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.sn_entry.bind("<Return>", lambda event: self.validate_sn())


        self.iv4_led = ctk.CTkButton(product_section, text="", width=30, height=30, fg_color="blue", corner_radius=15)
        self.iv4_led.grid(row=1, column=1, padx=10, pady=5)

        self.plc_button = ctk.CTkButton(product_section, text="", width=30, height=30, fg_color="blue", corner_radius=15)
        self.plc_button.grid(row=1, column=2, padx=10, pady=5)

        # ---- Log Information ----
        log_section = ctk.CTkFrame(right_frame, fg_color="#e6e6e6", corner_radius=8)
        log_section.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        log_section.grid_rowconfigure(1, weight=1)
        log_section.grid_columnconfigure(0, weight=1)

        log_label = ctk.CTkLabel(log_section, text="Log Information", font=("Arial", 14, "bold"))
        log_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.log_text = ctk.CTkTextbox(log_section)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.log_text.insert("end", "08:54:05: Aplicación SpecTrace iniciada.\n")


        # ---- Alarm Information ----
        alarm_section = ctk.CTkFrame(right_frame, fg_color="#e6e6e6", corner_radius=8)
        alarm_section.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        alarm_section.grid_rowconfigure(1, weight=1)
        alarm_section.grid_columnconfigure(0, weight=1)

        alarm_label = ctk.CTkLabel(alarm_section, text="Alarm Information", font=("Arial", 14, "bold"))
        alarm_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        alarm_text = ctk.CTkTextbox(alarm_section)
        alarm_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        alarm_text.insert("end", "08:54:05: Aplicación SpecTrace iniciada.\n")

        # ====== Intentar conectar al PLC ======
        #self.plc_link = PLCLink(self.update_plc_led, self.on_plc_fail)
        #self.plc_link.connect()




        # ====== Intentar conectar al Scanner =====
        self.scanner_link = ScannerLink(self.update_scanner_led, self.on_scanner_fail)
        self.start_scanner_connect()

    def log(self, msg:str):
        print(msg)
        self.after(0,lambda: (
            self.log_text.insert("end", msg + "\n"),
            self.log_text.see("end")
        ))


    def update_plc_led(self, status: bool):
        color = "green" if status else "blue"
        self.after(0, lambda: self.plc_button.configure(fg_color=color))

        # Si el PLC está ok y aún no intentamos el scanner, lánzalo:
        if status and not self.scanner_attempted:
            self.start_scanner_connect()

    # ----  ----
    def on_plc_fail(self):
        """Se ejecuta cuando falla la conexión al PLC"""
        msg = CTkMessagebox(
            title="PLC Connection",
            message="No se pudo conectar al PLC.\n¿Quieres reintentar o ir a Settings?",
            icon="cancel",
            option_1="Retry",
            option_2="Settings",
            option_3="Cancel"
        )
        response = msg.get()

        if response == "Retry":
            self.plc_link.connect()
        elif response == "Settings":
            PLCConfigWindow(self, on_close=self.retry_connection)  # abre ventana de configuración
        else:
            print("🚫 Usuario canceló el intento de conexión")

    def retry_connection(self):
        "Reintentar conexion al cerrar settings"
        self.plc_link.connect()

    def start_scanner_connect(self, force=False):
        """Conecta al scanner y enclava el LED en verde si tiene éxito."""
        if self.scanner_attempted and not force:
            return
        self.scanner_attempted = True
        self.scanner_link = ScannerLink(self.update_scanner_led, self.on_scanner_fail, self.on_scanner_data)
        self.scanner_link.connect()

    def update_scanner_led(self, ok: bool):
        color = "green" if ok else "red"
        # Para seguridad con hilos, usa after:
        self.after(0, lambda: self.iv4_led.configure(fg_color=color))


    # Validar inicial
    # ---- Nueva función en mainWindow ----
    def validate_sn(self, event=None):
        # 👇 limpiar tabla antes de empezar una nueva prueba
        for item in self.table.get_children():
            self.table.delete(item)

        serial = self.sn_entry.get().strip()
        if not serial.startswith("K"):  # 👈 validar primera letra
            CTkMessagebox(
                title="Invalid Serial",
                message="El número de serie debe iniciar con 'K'.\nPor favor vuelve a escanear.",
                icon="warning",
                option_1="OK"
            )
            self.sn_entry.delete(0, "end")  # limpiar para reintento
        else:
            print(f"✅ Serial válido: {serial}")

            # 👇 Confirmación antes de mandar trigger
            msg = CTkMessagebox(
                title="Confirmar montaje",
                message="¿La pieza ya está montada para inspección?",
                icon="question",
                option_1="Sí",
                option_2="No"
            )
            response = msg.get()

            if response == "Sí":
                if self.scanner_link and self.scanner_link.connected:
                    self.status_label.configure(text="Testing..", text_color="blue")
                    self.scanner_link.send_trigger()
                else:
                    CTkMessagebox(
                        title="Scanner Not Connected",
                        message="El escáner no está conectado.\nNo se pudo enviar trigger.",
                        icon="cancel",
                        option_1="OK"
                    )
            else:
                print("⚠️ Usuario indicó que la pieza no está lista.")



    def on_scanner_fail(self):
        """Se ejecuta cuando falla la conexión al Scanner"""
        msg = CTkMessagebox(
            title="Scanner Connection",
            message="No se pudo conectar al Scanner.\n¿Quieres reintentar o ir a Settings?",
            icon="cancel",
            option_1="Retry",
            option_2="Settings",
            option_3="Cancel"
        )
        response = msg.get()

        if response == "Retry":
            self.start_scanner_connect(force=True)
        elif response == "Settings":
            ScannerConfigWindow(self, on_close=self.retry_scanner_connection)  # abre ventana de configuración
        else:
            print("🚫 Usuario canceló el intento de conexión")
            self.destroy()
        self.update_scanner_led(False)

    def retry_scanner_connection(self):
        """Reintentar conexión al cerrar settings"""
        self.start_scanner_connect(force=True)
        #self.after(200, lambda: self.state("zoomed"))

    def get_unit_info(self, serial):
        try:
            if self.ff_client is None:
                self.ff_client = Client(self.ff_wsdl)

            response = self.ff_client.service.GetUnitInfo(
                serialNumber=serial,
                stationName=self.ff_station,
                userId=self.ff_user,
                extraData=""
            )
            self.log(f"📋 GetUnitInfo OK para {serial}")
            return response
        except Exception as e:
            self.log(f"❌ Error en GetUnitInfo: {e}")
            return None


    import time

    def show_latest_image(self, result_type):
        config = load_config()
        base_path = config.get("images", {}).get("path", "C:/SpecTrace/images")

        folder = os.path.join(base_path, result_type)
        if not os.path.exists(folder):
            print(f"⚠️ Carpeta no encontrada: {folder}")
            return

        files = glob.glob(os.path.join(folder, "*.bmp"))
        if not files:
            print(f"⚠️ No hay imágenes en {folder}")
            return

        latest_file = max(files, key=os.path.getmtime)
        print(f"📸 Mostrando imagen: {latest_file}")

        # ---- abrir con retry seguro ----
        img = None
        for attempt in range(3):  # 3 intentos
            try:
                img = Image.open(latest_file)
                img.load()  # forzar a que cargue completa
                break
            except Exception as e:
                print(f"⚠️ Error abriendo {latest_file}: {e} (intento {attempt + 1}/3)")
                time.sleep(0.5)  # espera 200 ms antes de reintentar

        if img is None:
            print(f"❌ No se pudo abrir la imagen {latest_file} después de 3 intentos")
            return

        # 🔹 función auxiliar para redimensionar y mostrar
        def resize_and_show(frame, label, image):
            w, h = frame.winfo_width(), frame.winfo_height()
            if w > 1 and h > 1:
                resized = image.resize((w, h), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(w, h))
                label.configure(image=ctk_img, text="")
                label.image = ctk_img  # mantener referencia

        resize_and_show(self.cam1_frame, self.cam1_label, img)
        resize_and_show(self.cam2_frame, self.cam2_label, img)

    def on_scanner_data(self, data: str):
        parts = data.split(",")
        if parts[0] == "RT" and len(parts) >= 6:
            message = parts[0]
            count = parts[1]
            result = parts[2]  # "OK" o "NG"
            cam_pos1 = parts[3]
            cam_res1 = parts[4]
            num_res1 = parts[5]

            self.table.insert("", "end", values=(
                message, count, result,
                cam_pos1, cam_res1, num_res1,
                "", "", ""
            ))

            if result in ("OK", "NG"):
                self.show_latest_image(result)

                # cambia status label
                if result == "OK":
                    self.status_label.configure(text="Testing...", text_color="blue")
                else:
                    self.status_label.configure(text="FAIL", text_color="red")
                    CTkMessagebox(
                        title="Test Result",
                        message="❌ FAIL: La pieza falló la prueba.",
                        icon="cancel",
                        option_1="OK"
                    )

                serial = self.sn_entry.get().strip()
                if serial:
                    self.get_unit_info(serial)  # consulta GetUnitInfo
                    self.save_result(serial, result)  # manda SaveResult
                    self.sn_entry.delete(0, "end")  # limpiar
        else:
            print("⚠️ Respuesta desconocida:", data)

    def build_fftester_xml(self, serial: str, status: str) -> str:
        # status debe ser "Passed" o "Failed"
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-06:00")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
    <BATCH TIMESTAMP="{ts}" SYNTAX_REV="1.3" COMPATIBLE_REV="1.1">
      <FACTORY NAME="AT/ALT" LINE="Prodline" TESTER="{self.ff_station}" FIXTURE="" SHIFT="" USER="{self.ff_user}" SYSTEMTYPE="FTS" TESTCATEGORY="FT"/>
      <PRODUCT NAME="GenericProduct" REVISION="V1.0" FAMILY="" CUSTOMER=""/>
      <PANEL ID="Undef" COMMENT="" RUNMODE="Production"
             TIMESTAMP="{ts}"
             TESTTIME="1.0"
             WAITTIME="0.0"
             STATUS="{status}">
        <DUT ID="{serial}" COMMENT="" PANEL="0" SOCKET="0"
             TIMESTAMP="{ts}"
             TESTTIME="1.0"
             STATUS="{status}">
          <GROUP NAME="Parametrics" STEPGROUP="Main" GROUPINDEX="0" LOOPINDEX="-1"
                 TYPE="SequenceCall" RESOURCE="AutoSequence"
                 MODULETIME="1.0" TOTALTIME="1.0"
                 TIMESTAMP="{ts}"
                 STATUS="{status}">
            <TEST NAME="Leak" DESCRIPTION="" UNIT="sccm" VALUE="12.3"
                  HILIM="20" LOLIM="0"
                  STATUS="{status}" RULE="GTLT" TARGET=""
                  DATATYPE="Number"/>
            <TEST NAME="Firmware" DESCRIPTION="" UNIT="" VALUE="V1.8"
                  HILIM="" LOLIM=""
                  STATUS="{status}" RULE="EQ" TARGET=""
                  DATATYPE="String"/>
          </GROUP>
        </DUT>
      </PANEL>
    </BATCH>
    """

    def save_result(self, serial: str, result_token: str):
        """Lanza thread para mandar SaveResult con Passed/Failed según result_token (OK/NG)."""
        status = "Passed" if result_token == "OK" else "Failed"
        threading.Thread(
            target=self._save_result_worker,
            args=(serial, status),
            daemon=True
        ).start()

    def _save_result_worker(self, serial: str, status: str):
        try:
            if self.ff_client is None:
                self.ff_client = Client(self.ff_wsdl)

            xml_payload = self.build_fftester_xml(serial, status)
            self.log(f"⬆️ Enviando SaveResult ({status}) para {serial}...")

            resp = self.ff_client.service.SaveResult(
                ffTesterXmlRequest=xml_payload,
                stationName=self.ff_station,
                userId=self.ff_user,
                extraData=""
            )

            value = getattr(resp, "Value", None) or resp.get("Value")
            if value == "Success":
                # 👇 Solo aquí confirmamos PASS/FAIL
                if status == "Passed":
                    self.log(f"✅ Test PASSED confirmado por FFTester para {serial}")
                    self.status_label.configure(text="Pass", text_color="green")
                else:
                    self.log(f"❌ Test FAILED confirmado por FFTester para {serial}")
            else:
                self.log(f"⚠️ SaveResult rechazado para {serial}: {value}")
                #self.log(f"📝 Respuesta completa: {resp}")
                self.status_label.configure(text="Fail", text_color="red")

        except Exception as e:
            self.log(f"❌ SaveResult error: {e}")
