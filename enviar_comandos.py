import serial
import time

def interactive_console(port, baudrate):
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
    interactive_console("COM5", 9600) 
