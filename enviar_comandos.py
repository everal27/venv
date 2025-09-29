import serial
import serial.tools.list_ports
import time

def detectar_puerto():
    """Detecta automáticamente el primer puerto serie disponible"""
    puertos = list(serial.tools.list_ports.comports())

    if not puertos:
        print("❌ No se detectaron dispositivos conectados.")
        return None

    print("🔎 Puertos detectados:")
    for i, p in enumerate(puertos):
        print(f"{i+1}. {p.device} - {p.description}")

    # Si hay más de un puerto, elegir el primero automáticamente
    # (puedes modificar para pedir al usuario elegir)
    return puertos[0].device  

def interactive_console(baudrate=9600):
    port = detectar_puerto()
    if port is None:
        return

    try:
        # Abrir puerto serial
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Conectado al puerto {port} (baudrate {baudrate})")
        print("Escribe comandos para enviar al router. Escribe 'exit' para salir.\n")

        while True:
            comando = input("Router> ")  # Leer comando desde la terminal
            
            if comando.lower() == "exit":
                print("🔌 Cerrando conexión...")
                break

            # Enviar comando al router
            ser.write(f"{comando}\r\n".encode())
            time.sleep(1)

            # Leer salida del router
            output = ser.read_all().decode(errors="ignore")
            print(output)

        ser.close()

    except serial.SerialException as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == "__main__":
    interactive_console(9600)
