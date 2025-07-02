import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")

rooms = {} #{room1:{creator:name, noOfActiveUsers:2, users:[user1,user2]}
def createRoom(conn,name):
    conn.send("Enter room name ".encode())
    roomName = conn.recv(1024).decode()
    rooms[roomName] = {'creator':name, 'users':[],'noOfActiveUsers':0}
    conn.send(f'created room {roomName}'.encode())

def joinRoom(conn,name):
    conn.send('Enter room name'.encode())
    roomName = conn.recv(1024).decode()
    if roomName in rooms.keys():
        rooms[roomName]['users'].append(name)
        conn.send((f'Joined Room {roomName}').encode())
        return roomName

def broadcast(conn,sender,msg,roomName):
    msg = sender + '>' + msg
    for user in rooms[roomName]['users'] :
        userConn = userList[user]
        if userConn != conn:            
            userConn.send(msg.encode())


def handleClient(conn,addr,name):
    conn.send(f'\nHello {name} \n'.encode())
    joinedRoom = False
    while True:
        conn.send('\nEnter 1. to create room 2. to join room '.encode())
        choice = conn.recv(1024).decode()
        if choice == '1':
            createRoom(conn,name)
        elif choice == '2':
            joinedRoom = True
            roomName = joinRoom(conn,name)
            break
        else:
            conn.send('\nwrong choice'.encode())

    while joinedRoom:

        conn.send('\nEnter 0.To exit 1.To Chat 2.To see all active users 3.To see number of active users 4.To see most active Users'.encode())
        choice = conn.recv(1024).decode()
        if choice == '1':
            while True:            
                msg = conn.recv(1024).decode()
                if not msg:
                    break
                if msg == '0':
                    break
                broadcast(conn,name,msg,roomName)

        elif choice == '0':
            rooms[roomName]['users'].remove(name)
            break
        elif choice == '2':
            for user in rooms[roomName]['users']:
                conn.send(f'\n{user}'.encode())
        elif choice == '3':
            l = len(rooms[roomName]['users'])
            conn.send(str(l).encode())
        else:
            conn.send('\nWrong Choice'.encode())


        
    conn.close()
    print(name, 'exited')

userList = {}
while True:
    try:
        conn, addr = server.accept()    # addr = (client_ip, client_port)
        name = conn.recv(1024).decode()
        userList[name] = conn
        threading.Thread(target=handleClient, args=(conn,addr,name)).start()
    except:
        break


