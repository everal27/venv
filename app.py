import socket
print ("hello world")

hostname = socket.gethostname()
print(f"Hostname: {hostname}")

IPaddress = socket.gethostbyname(hostname)
print(f"IP Address: {IPaddress}")