import serial
import time


def configure_device(port, baurderate, com, hostname, username, password):
    try:
        ser = serial.Serial(port, baurderate, timeout=1)
        ser.write(f"{com}\r\n".encode())
        time.sleep(1) 
        ser.write(f"eneale\r\n".encode())  
        time.sleep(1)
        ser.write(f"configure terminal\r\n".encode())
        time.sleep(1)
        ser.write(f"hostame{hostname}\r\n".encode())
        time.sleep(1)
        ser.write(f"username {username} privilege 15 secret {password}\r\n".encode())
        time.sleep(1)
        ser.write(f"ip domain-name example.com\r\n".encode())
        time.sleep(1)
        ser.write(f"crypto key generate rsa 1024\r\n".encode())
        time.sleep(1)
        ser.write(f"line vty 0 4\r\n".encode())
        time.sleep(1)
        ser.write(f"login local\r\n".encode())
        time.sleep(1)
        ser.write(f"transport input ssh\r\n".encode())
        time.sleep(1)
        ser.write(f"transport output ssh\r\n".encode())
        time.sleep(1)
        ser.write(f"exit\r\n".encode()) 
        time.sleep(1)
        ser.write(f"console line 0\r\n".encode())
        time.sleep(1)
        ser.write(f"login local\r\n".encode())
        time.sleep(1)
        ser.write(f"exit\r\n".encode())
        time.sleep(1)
        ser.write(f"write memory\r\n".encode())
        time.sleep(1)
    except serial.SerialException as e:
        print(f"Error: {e}")
        
R1 = configure_device("COM3", 9600, "R1", "cisco", "cisco", "simon.com")