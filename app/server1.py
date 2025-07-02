import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")


def broadcast(conn,addr,msg):
    for client in users :
        if client != conn:
            client.send(msg.encode())


def handleClient(conn,addr):
    broadcast(conn,addr,msg)
    while True:
        msg = conn.recv(1024).decode()
        broadcast(conn,addr,msg)

users = []
while True:
    try:
        conn, addr = server.accept()
        users.append(conn)
        threading.Thread(target=handleClient, args=(conn,addr)).start()
    except:
        break


