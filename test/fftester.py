from zeep import Client

# URL del WSDL
wsdl_url = "http://10.106.230.168:9500/FFTester/?wsdl"

# Crear cliente SOAP
client = Client(wsdl=wsdl_url)

# Parámetros correctos para GetUnitInfo
params = {
    "serialNumber": "GLBFLG254000336",   # serial real de la unidad
    "stationName": "PHI-AXI",  # estación que hace la petición
    "userId": "Admin",             # usuario que manda la petición
    "extraData": ""                # en blanco si no se ocupa
}
#params = {
#    "serialNumber": "FLG2540-00360",   # serial real de la unidad
#    "stationName": "PHI-TLA-TEMPERATURE-VALIDATION-MAP",  # estación que hace la petición
#    "userId": "Admin",             # usuario que manda la petición
#    "extraData": ""                # en blanco si no se ocupa
#}

# Llamar al servicio
response = client.service.GetUnitInfo(**params)

print("Respuesta del servicio:")
print(response)