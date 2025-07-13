# client.py

import socket
import threading

def recv(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            break

def send(sock):
    while True:
        try:
            msg = input()
            sock.send(msg.encode())
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5050))

recv_thread = threading.Thread(target=recv, args=(client,))
send_thread = threading.Thread(target=send, args=(client,))
recv_thread.start()
send_thread.start()
