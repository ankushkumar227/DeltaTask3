import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost',5050))

def send():
    while True:
        msg = input(">")
        client.send(msg.encode())

def recv():
    while True:
        msg = client.recv(1024).decode()
        print(msg)


threading.Thread(target=send).start()
threading.Thread(target=recv).start()






