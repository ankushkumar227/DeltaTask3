import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost',5050))
client.send("yeah".encode())

response = client.recv(1024).decode()
print('received ', response)

