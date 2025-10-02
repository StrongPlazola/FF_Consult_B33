import snap7
from snap7.util import get_bool

# Conexión al LOGO
plc = snap7.client.Client()
plc.connect("192.168.0.3", 0, 1)   # IP del LOGO, rack=0, slot=1

# Leer un byte del área de memoria (Merker)
# Parámetros: área, DB número, start, size
# MK = área de merkers, DB=0, dirección inicial=0, tamaño=1 byte
data = plc.read_area(snap7.type.Areas.MK, 0, 0, 1)

# Obtener el bit 0 del byte leído (M0.0)
estado = get_bool(data, 0, 0)

print("M0.0 =", estado)

# Cerrar conexión
plc.disconnect()