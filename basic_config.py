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

    # Elegir automáticamente el primer puerto detectado
    return puertos[0].device  

def configure_device(baudrate, hostname, username, password, domain):
    port = detectar_puerto()
    if port is None:
        return

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Conectado al puerto {port} para configurar el dispositivo.")

        comandos = [
            "en",
            "configure terminal",
            f"hostname {hostname}",
            f"username {username} privilege 15 secret {password}",
            f"ip domain-name {domain}",
            "crypto key generate rsa",
            "1024",
            "line vty 0 4",
            "login local",
            "transport input ssh",
            "transport output ssh",
            "exit",
            "line console 0",
            "login local",
            "exit",
            "exit",
            "write memory"
        ]

        for cmd in comandos:
            ser.write(f"{cmd}\r\n".encode())
            time.sleep(1)  # Espera para que el router procese cada comando

        ser.close()
        print("✅ Configuración completada y guardada en el dispositivo.")

    except serial.SerialException as e:
        print(f"❌ Error: {e}")

# Llamada a la función sin especificar puerto
configure_device(9600, "R1", "cisco", "cisco", "simon.com")
