from datetime import datetime
import socket
import threading
import mysql.connector

current_time = datetime.now().strftime("%H:%M:%S") #current time in mysql table format

myconn = mysql.connector.connect(
    host = 'localhost',
    user = 'Ankush',
    password = 'Elon@2005',
    database = 'chatServer'
)

cursor = myconn.cursor()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")

def broadcast(conn,sender,msg,roomName):
    current_time = datetime.now().strftime("%H:%M:%S")
    cursor.execute("""
        insert into chat-history (room, sender, msg, time)
        values (%s,%s,%s,%s)
    """,(roomName, sender,msg,current_time))
    
    cursor.execute("SELECT username FROM users WHERE current_room = %s", (roomName,))
    rows = cursor.fetchall()

    formatMsg = sender + '>' + msg
    for user in rows :  # user is a tuple 
        userConn = userList[user[0]]
        if userConn != conn:            
            userConn.send(formatMsg.encode())
                                                                                                                                                                                                                                                    
def createRoom(conn,userName):
    conn.send("Enter room name ".encode())
    roomName = conn.recv(1024).decode()
    current_time = datetime.now().strftime("%H:%M:%S")
    cursor.execute("""INSERT INTO rooms (roomName, created_by, created_at) 
                   VALUES (%s, %s, %s)", (roomName, userName, current_time))""")
    myconn.commit()
    conn.send(f'created room {roomName}'.encode())
    myconn.commit()

def joinRoom(conn,userName):

    cursor.execute("select roomName from rooms")
    rows = cursor.fetchall()
    rooms = [row[0] for row in rows]  # because fetch al returns list of tuples , each tuple representing a row

    if not rows:
        conn.send('No rooms available. Please create one.\n'.encode())
        return None
        
    conn.send('\nAvailable Rooms:\n'.encode())
    for room in rooms:
        conn.send(f'{room}\n'.encode())

    conn.send('Enter room name'.encode())
    roomName = conn.recv(1024).decode()

    if roomName in rooms:
        cursor.execute("""
            INSERT INTO users (username, current_room) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE current_room = %s
        """, (userName, roomName, roomName))

        msg = f"{userName} joined {roomName}"
        broadcast(conn,"System",msg,roomName)

        return roomName
    
def leaveRoom(conn,userName,roomName):
    cursor.execute("""update users set current_room = NULL where userName = %s""", (userName,))
    myconn.commit()
    sender = "System"
    msg = f"{userName} left {roomName}"

    broadcast(conn,"System",msg,roomName)






def handleClient(conn,addr,userName):
    conn.send(f'\nHello {userName} \n'.encode())
    joinedRoom = False
    while True:
        conn.send('\n--- Main Menu ---\n1. Create Room\n2. Join Room\nChoice: '.encode())
        choice = conn.recv(1024).decode()
        if choice == '1':
            createRoom(conn,userName)
        elif choice == '2':
            joinedRoom = True
            roomName = joinRoom(conn,userName)
            break
        else:
            conn.send('\nwrong choice'.encode())

    while joinedRoom:

        conn.send('\nEnter \n0.To exit \n1.To Chat \n2.To see all active users \n3.To see number of active users'.encode())
        choice = conn.recv(1024).decode()
        if choice == '1':
            while True:            
                msg = conn.recv(1024).decode()
                if not msg:
                    break
                if msg == '0':
                    break
                broadcast(conn,userName,msg,roomName)

        elif choice == '0':
            leaveRoom(conn,userName,roomName)
            break
        elif choice == '2':
            cursor.execute("SELECT username FROM users WHERE current_room = %s,(roomName,)")
            rows = cursor.fetchall()
            for user in rows:
                conn.send(f'\n{user[0]}'.encode())
        elif choice == '3':
            cursor.execute("SELECT count(username) FROM users WHERE current_room = %s,(roomName,)")
            count = cursor.fetchone()[0]
            conn.send(str(count).encode())
        else:
            conn.send('\nWrong Choice'.encode())


    cursor.execute("DELETE FROM users WHERE username = %s", (userName,))    
    conn.close()
    print(userName, 'exited')

userList = {}
while True:
    try:
        conn, addr = server.accept()    # addr = (client_ip, client_port)
        name = conn.recv(1024).decode()
        if name in userList:
            conn.send('User already exist. Try another username'.encode())
            conn.close()
            continue
        userList[name] = conn
        cursor.execute("INSERT INTO users (username, current_room) VALUES (%s, NULL)", (name,))
        myconn.commit()
        threading.Thread(target=handleClient, args=(conn,addr,name)).start()
    except:
        break


