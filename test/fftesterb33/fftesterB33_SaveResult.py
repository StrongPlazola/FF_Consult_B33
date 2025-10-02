import datetime
from lxml import etree
from zeep import Client

# ==============================
# CONFIG
# ==============================
WSDL_URL = "http://10.106.237.111:9000/FFTester/?wsdl"
STATION = "BSLT-NESTS009"
USER = "Admin"
SERIAL = "K441M18295 2082501719662VAKT7-2"

# ==============================
# XML GENERADOR
# ==============================
def build_xml(serial):
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-06:00")

    xml_str = f"""<?xml version="1.0" encoding="UTF-8"?>
<BATCH TIMESTAMP="{ts}" SYNTAX_REV="1.3" COMPATIBLE_REV="1.1">
  <FACTORY NAME="AT/ALT" LINE="Prodline" TESTER="{STATION}" FIXTURE="" SHIFT="" USER="{USER}" SYSTEMTYPE="FTS" TESTCATEGORY="FT"/>
  <PRODUCT NAME="GenericProduct" REVISION="V1.0" FAMILY="" CUSTOMER=""/>
  <PANEL ID="Undef" COMMENT="" RUNMODE="Production"
         TIMESTAMP="{ts}"
         TESTTIME="1.0"
         WAITTIME="0.0"
         STATUS="Passed">
    <DUT ID="{serial}" COMMENT="" PANEL="0" SOCKET="0"
         TIMESTAMP="{ts}"
         TESTTIME="1.0"
         STATUS="Passed">
      <GROUP NAME="Parametrics" STEPGROUP="Main" GROUPINDEX="0" LOOPINDEX="-1"
             TYPE="SequenceCall" RESOURCE="AutoSequence"
             MODULETIME="1.0" TOTALTIME="1.0"
             TIMESTAMP="{ts}"
             STATUS="Passed">
        <TEST NAME="Leak" DESCRIPTION="" UNIT="sccm" VALUE="12.3"
              HILIM="20" LOLIM="0"
              STATUS="Passed" RULE="GTLT" TARGET=""
              DATATYPE="Number"/>
        <TEST NAME="Firmware" DESCRIPTION="" UNIT="" VALUE="V1.8"
              HILIM="" LOLIM=""
              STATUS="Passed" RULE="EQ" TARGET=""
              DATATYPE="String"/>
      </GROUP>
    </DUT>
  </PANEL>
</BATCH>
"""
    return xml_str

# ==============================
# MAIN
# ==============================
def main():
    client = Client(WSDL_URL)
    xml_payload = build_xml(SERIAL)

    # Validación rápida de XML antes de enviar
    try:
        etree.fromstring(xml_payload.encode("utf-8"))
        print("✅ XML válido localmente")
    except Exception as e:
        print("❌ Error validando XML:", e)
        return

    # Llamada al servicio SaveResult
    response = client.service.SaveResult(
        ffTesterXmlRequest=xml_payload,
        stationName=STATION,
        userId=USER,
        extraData=""
    )

    print("📋 Respuesta SaveResult:")
    print(response)

if __name__ == "__main__":
    main()