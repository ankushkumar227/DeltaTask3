import socket
import threading

name = input('Enter name ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost',5050))
client.send(name.encode())


def send():

   while True:
        msg = input()
        if msg == 'exit':
            client.close()
            break
        client.send(msg.encode())

def recv():
    while True:
        try:
            msg = client.recv(1024).decode()
            print(msg)
        except Exception as e:
            print(f"recv() exited due to error")
            break


threading.Thread(target=send).start()
threading.Thread(target=recv).start()











