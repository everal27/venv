import csv
import serial
import time
import re

# Regex para validar puerto y dominio
REGEX_PORT = re.compile(r"^COM\d+$")
REGEX_DOMAIN = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Regex para extraer modelo y versión desde "show version"
REGEX_VERSION = re.compile(r"Version\s+([\d.()A-Za-z]+)")
REGEX_MODEL = re.compile(r"cisco\s+(\S+)\s+\(")

# ==============================
# Funciones
# ==============================
def conectar_router(port, baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Conectado al puerto {port}")
        return ser
    except serial.SerialException as e:
        print(f"❌ Error al abrir {port}: {e}")
        return None

def enviar_comando(ser, comando, espera=2):
    ser.write(f"{comando}\r\n".encode())
    time.sleep(espera)
    salida = ser.read_all().decode(errors="ignore")
    return salida

# ==============================
# Procesar CSV y generar resultados
# ==============================
def procesar_csv(ruta_csv, ruta_resultados="routers_resultados.csv"):
    resultados = []

    try:
        with open(ruta_csv, mode="r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            for row in lector:
                serie = row.get("Serie", "")
                port = row.get("Port", "")
                device = row.get("Device", "")
                ip_domain = row.get("Ip-domain", "")
                modelo_esperado = row.get("Modelo", "N/A")
                version_esperada = row.get("Version", "N/A")

                print(f"\n🔹 Procesando router {device} ({serie})...")

                # Validaciones
                if not REGEX_PORT.match(port):
                    print(f"⚠ Puerto '{port}' inválido. Saltando router.")
                    resultados.append({
                        **row, "Modelo_detectado": "N/A", "Version_detectada": "N/A",
                        "Modelo_coincide": "No", "Version_coincide": "No"
                    })
                    continue

                if not REGEX_DOMAIN.match(ip_domain):
                    print(f"⚠ Dominio '{ip_domain}' inválido. Saltando router.")
                    resultados.append({
                        **row, "Modelo_detectado": "N/A", "Version_detectada": "N/A",
                        "Modelo_coincide": "No", "Version_coincide": "No"
                    })
                    continue

                # Conectar
                ser = conectar_router(port)
                if ser:
                    salida = enviar_comando(ser, "show version")

                    # Extraer modelo y versión detectados
                    version_match = REGEX_VERSION.search(salida)
                    model_match = REGEX_MODEL.search(salida)

                    version_detectada = version_match.group(1) if version_match else "Desconocida"
                    modelo_detectado = model_match.group(1) if model_match else "Desconocido"

                    modelo_coincide = "Sí" if modelo_esperado == modelo_detectado else "No"
                    version_coincide = "Sí" if version_esperada == version_detectada else "No"

                    print(f"--- Resultado show version de {device} ---")
                    print(f"Modelo esperado: {modelo_esperado} | Detectado: {modelo_detectado} | Coincide: {modelo_coincide}")
                    print(f"Versión esperada: {version_esperada} | Detectada: {version_detectada} | Coincide: {version_coincide}")

                    ser.close()
                    print(f"🔌 Conexión con {device} cerrada")

                    resultados.append({
                        **row,
                        "Modelo_detectado": modelo_detectado,
                        "Version_detectada": version_detectada,
                        "Modelo_coincide": modelo_coincide,
                        "Version_coincide": version_coincide
                    })
                else:
                    print(f"⚠ No se pudo conectar al router {device}")
                    resultados.append({
                        **row, "Modelo_detectado": "N/A", "Version_detectada": "N/A",
                        "Modelo_coincide": "No", "Version_coincide": "No"
                    })

        # Guardar resultados en un CSV
        campos = list(lector.fieldnames) + ["Modelo_detectado", "Version_detectada", "Modelo_coincide", "Version_coincide"]
        with open(ruta_resultados, mode="w", newline="", encoding="utf-8") as res_file:
            escritor = csv.DictWriter(res_file, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(resultados)

        print(f"\n✅ Resultados guardados en '{ruta_resultados}'")

    except Exception as e:
        print(f"❌ Error al procesar el CSV: {e}")

# ==============================
# Ejecutar script automáticamente
# ==============================
if __name__ == "__main__":
    procesar_csv("modelos.csv")
