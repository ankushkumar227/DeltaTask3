import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")

conn, addr = server.accept()
print('connection from adress ', addr)

data = conn.recv(1024).decode()
print('received ', data)

conn.send("hello".encode())

conn.close()
server.close()

