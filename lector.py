import csv
import serial
import time
import re
import os
from basic_config import configure_device

# ==============================
# Regex
# ==============================
REGEX_VERSION = re.compile(r"Version\s*[:]*\s*([0-9A-Za-z\.\(\)\-_,]+)", re.IGNORECASE)
REGEX_MODEL_PAREN = re.compile(r"\(([^)]+)\)\s*,\s*Version", re.IGNORECASE)
REGEX_SERIAL = re.compile(r"(?:System serial number\s*:\s*|Processor board ID\s*)(\S+)", re.IGNORECASE)

# ==============================
# Funciones auxiliares
# ==============================
def read_until_idle(ser, idle_timeout=1.2, overall_timeout=10):
    buf = bytearray()
    start = time.time()
    last = time.time()
    while True:
        chunk = ser.read(1024)
        if chunk:
            buf.extend(chunk)
            last = time.time()
            if b'--More--' in chunk:
                ser.write(b' ')
                time.sleep(0.2)
        else:
            if time.time() - last > idle_timeout: break
            if time.time() - start > overall_timeout: break
            time.sleep(0.05)
    return buf.decode(errors="ignore")

def send_command(ser, cmd, espera=0.3):
    ser.write((cmd + "\r\n").encode())
    time.sleep(espera)
    return read_until_idle(ser)

def extraer_datos(salida):
    m_model = REGEX_MODEL_PAREN.search(salida)
    modelo = m_model.group(1).strip() if m_model else "Desconocido"
    m_ver = REGEX_VERSION.search(salida)
    version = m_ver.group(1).strip() if m_ver else "Desconocida"
    m_ser = REGEX_SERIAL.search(salida)
    serial = m_ser.group(1).strip() if m_ser else "Desconocido"
    return modelo, version, serial

def conectar_router(port, baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return ser
    except Exception as e:
        print(f"❌ No se pudo abrir {port}: {e}")
        return None

# ==============================
# Función principal
# ==============================
def procesar_csv(ruta_csv, ruta_resultados="routers_resultados.csv"):
    if not os.path.exists(ruta_csv):
        with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Serie","Port","Device","User","Password","Ip-domain","Modelo","Version"])
            writer.writeheader()

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        lector = list(csv.DictReader(f))

    resultados = []
    puertos = set(row["Port"] for row in lector if row.get("Port"))

    for port in puertos:
        print(f"\n=== Escaneando {port} ===")
        ser = conectar_router(port)
        if not ser:
            continue

        try:
            send_command(ser, "terminal length 0")
            salida = send_command(ser, "show version", espera=1.0)
            modelo, version, serial_detectado = extraer_datos(salida)

            print(f"🔎 Detectado en {port}: Serial={serial_detectado}, Modelo={modelo}, Versión={version}")

            fila = next((row for row in lector if row["Serie"] == serial_detectado and row["Port"] == port), None)

            if fila:
                # Validación estricta: Serial + Modelo + Versión
                if fila.get("Modelo","") == modelo and fila.get("Version","") == version:
                    resultados.append({
                        **fila,
                        "Modelo_detectado": modelo,
                        "Version_detectada": version,
                        "Serie_detectada": serial_detectado,
                        "Modelo_coincide": "Sí",
                        "Version_coincide": "Sí"
                    })
                    print(f"✅ Coincidencia total. Aplicando configuración inicial a {fila['Device']}...")
                    configure_device(
                        port,
                        9600,
                        fila.get("Device","Router"),
                        fila.get("User","cisco"),
                        fila.get("Password","cisco"),
                        fila.get("Ip-domain","cisco.local")
                    )
                else:
                    resultados.append({
                        **fila,
                        "Modelo_detectado": modelo,
                        "Version_detectada": version,
                        "Serie_detectada": serial_detectado,
                        "Modelo_coincide": "No",
                        "Version_coincide": "No"
                    })
                    print(f"⚠ Coincidencia parcial. No se aplica configuración.")
            else:
                print(f"❌ Serial {serial_detectado} no está en CSV. Se omite configuración.")

        finally:
            ser.close()

    # Guardar resultados en CSV
    if resultados:
        campos = list(resultados[0].keys())
        with open(ruta_resultados, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\n✅ Resultados guardados en {ruta_resultados}")

# ==============================
# Ejecutar script
# ==============================
if __name__ == "__main__":
    procesar_csv("modelos.csv")
