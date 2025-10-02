import pyodbc

def is_unit_at_station(serial: str, station_to_check: str):
    server = "10.106.254.134,15001"
    database = "p_DevitoGDLB33"
    username = "Devito2025"
    password = "p2Cvu1XG82dE"

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password};"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # 1) Buscar UnitID en ffSerialNumber
    cursor.execute("SELECT TOP 1 UnitID FROM ffSerialNumber WHERE Value = ?", (serial,))
    row = cursor.fetchone()
    if not row:
        return {"error": f"❌ Serial {serial} no encontrado"}
    unit_id = row.UnitID

    # 2) Última estación registrada en ffUnitStatusHistory
    cursor.execute("""
        SELECT TOP 1 h.StationID, s.Description AS StationName, h.Time
        FROM ffUnitStatusHistory h
        JOIN ffStation s ON h.StationID = s.ID
        WHERE h.UnitID = ?
        ORDER BY h.Time DESC
    """, (unit_id,))
    last_station = cursor.fetchone()

    cursor.close()
    conn.close()

    if not last_station:
        return {"error": f"⚠️ No hay historial de estaciones para UnitID {unit_id}"}

    current_station_name = last_station.StationName

    # 3) Comparar con la estación que evaluamos
    if current_station_name.strip().upper() == station_to_check.strip().upper():
        return {"result": True, "message": f"✅ El serial {serial} está en {station_to_check}"}
    else:
        return {
            "result": False,
            "message": f"❌ El serial {serial} NO está en {station_to_check}, está en {current_station_name}"
        }


# ================================
# Ejemplo de uso
# ================================
if __name__ == "__main__":
    serial = "K441M18295 2082501719662VAKT7-2"
    station_to_check = "DVTopSide_PyramidPlateCheck"

    result = is_unit_at_station(serial, station_to_check)
    print(result["message"])