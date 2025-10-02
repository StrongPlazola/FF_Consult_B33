from zeep import Client

# URL del nuevo WSDL
wsdl = "http://10.106.237.111:9000/FFTester/?wsdl"

# Crear cliente
client = Client(wsdl=wsdl)

# Datos de prueba
serial = "K441M18295 2082501719662VAKT7-2"
station = "BSLT-NESTS009"
user = "Admin"
extra = ""

# Llamar GetUnitInfo
try:
    response = client.service.GetUnitInfo(
        serialNumber=serial,
        stationName=station,
        userId=user,
        extraData=extra
    )
    print("📋 Respuesta GetUnitInfo:")
    print(response)
except Exception as e:
    print("❌ Error en GetUnitInfo:", e)