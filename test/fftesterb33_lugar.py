import pyodbc
from datetime import datetime
import pytz
from pathlib import Path

# 🔑 Conexión (ajusta si cambias user/pass)
CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=10.106.254.134,15001;"
    "DATABASE=p_DevitoGDLB33;"
    "UID=Devito2025;"
    "PWD=p2Cvu1XG82dE;"
    "TrustServerCertificate=yes;"
)

def iso_now():
    """Fecha en ISO 8601 con zona horaria (ej: 2025-10-01T12:59:00-06:00)."""
    tz = pytz.timezone("America/Mexico_City")
    return datetime.now(tz).isoformat(timespec="seconds")

def xml_con_parametros(
    serial: str,
    station: str,
    user: str = "Admin",
    status_panel: str = "Passed",
    status_dut: str = "Passed",
    mediciones: list | None = None,
) -> str:
    """Construye XML con resultados y mediciones paramétricas"""
    now = iso_now()
    if mediciones is None:
        mediciones = [
            {
                "name": "Tightness",
                "value": 64.5977,
                "unit": "Pa",
                "lo": 0.1,
                "hi": 200,
                "rule": "GTLT",
                "datatype": "Number",
                "status": "Passed",
            }
        ]

    tests_xml = []
    for m in mediciones:
        name = m.get("name", "Param")
        val = m.get("value", "")
        unit = m.get("unit", "")
        lo = m.get("lo", "")
        hi = m.get("hi", "")
        rule = m.get("rule", "EQ")
        dtype = m.get("datatype", "Number")
        st = m.get("status", "Passed")

        hi_str, lo_str = (str(hi) if hi != "" else ""), (str(lo) if lo != "" else "")
        tests_xml.append(
            f'<TEST NAME="{name}" DESCRIPTION="" UNIT="{unit}" VALUE="{val}" '
            f'HILIM="{hi_str}" LOLIM="{lo_str}" STATUS="{st}" RULE="{rule}" TARGET="" DATATYPE="{dtype}"/>'
        )

    tests_block = "\n        ".join(tests_xml)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<BATCH TIMESTAMP="{now}" SYNTAX_REV="1.3" COMPATIBLE_REV="1.1">
  <FACTORY NAME="AT/ALT" LINE="Prodline" TESTER="{station}" FIXTURE="" SHIFT="" USER="{user}" SYSTEMTYPE="FTS" TESTCATEGORY="FT"/>
  <PRODUCT NAME="GenericProduct" REVISION="V1.0" FAMILY="" CUSTOMER=""/>
  <PANEL ID="Undef" COMMENT="" RUNMODE="Production" TIMESTAMP="{now}" TESTTIME="1.0" STATUS="{status_panel}">
    <DUT ID="{serial}" COMMENT="" PANEL="0" SOCKET="0" TIMESTAMP="{now}" TESTTIME="1.0" STATUS="{status_dut}">
      <GROUP NAME="Parametrics" STEPGROUP="Main" GROUPINDEX="0" LOOPINDEX="-1" TYPE="SequenceCall" RESOURCE="AutoSequence" MODULETIME="1.0" TOTALTIME="1.0" TIMESTAMP="{now}" STATUS="{status_dut}">
        {tests_block}
      </GROUP>
    </DUT>
  </PANEL>
</BATCH>"""

def save_result(xml_str: str, save_path: str = "resultado.xml"):
    """Guarda el XML en archivo y lo envía a la BD"""
    # 1) Guardar a archivo para inspección
    Path(save_path).write_text(xml_str, encoding="utf-8")
    print(f"💾 XML guardado en {save_path}")

    # 2) Mandar a SQL
    enter = datetime.now()
    exit_ = enter
    with pyodbc.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.execute("EXEC udpTSKSaveTestResult ?, ?, ?", (xml_str, enter, exit_))
        conn.commit()
        print("✅ SaveResult ejecutado en BD")

# === Ejemplo de uso ===
if __name__ == "__main__":
    serial = "K441M18295 2082501719662VAKT7-2"
    station = "BSLT-NESTS009"
    mediciones = [
        {"name":"Leak","value":12.3,"unit":"sccm","lo":0,"hi":20,"rule":"GTLT","datatype":"Number","status":"Passed"},
        {"name":"Firmware","value":"V1.8","datatype":"String","status":"Passed"},
    ]

    xml = xml_con_parametros(serial, station, user="Admin", status_panel="Passed", status_dut="Passed", mediciones=mediciones)
    save_result(xml, "resultado.xml")