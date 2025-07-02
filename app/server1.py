import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")


def broadcast(conn,sender,msg):
    for client in users :
        if client != conn:            
            client.send(msg.encode())


def handleClient(conn,addr):
    sender = addr[1]
    while True:
        msg = conn.recv(1024).decode()
        if not msg:
            break
        if msg == 'exit':
            break
        broadcast(conn,sender,msg)
    if conn in users:
        users.remove(conn)
    conn.close()
    print(sender, 'exited')

users = []
while True:
    try:
        conn, addr = server.accept()    # addr = (client_ip, client_port)
        users.append(conn)
        print(addr)
        threading.Thread(target=handleClient, args=(conn,addr)).start()
    except:
        break


