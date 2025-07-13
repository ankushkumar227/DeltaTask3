# server.py

import socket
import threading
from datetime import datetime
import mysql.connector
import hashlib
import os

def hashed(password):
    return hashlib.sha256(password.encode()).hexdigest()

myconn = mysql.connector.connect(
    host='mysql-service',
    user='Ankush',
    password='Elon@2005',
    database='chatServer'
)
cursor = myconn.cursor()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 5050))
server.listen()

print("Server started...")

userList = {}  # {username: conn}
lock = threading.Lock()

def broadcast(sender, msg, room_name):
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO chat_history (room_name, sent_by, msg, sent_at) VALUES (%s, %s, %s, %s)", (room_name, sender, msg, sent_at))
    myconn.commit()

    cursor.execute("SELECT user_name FROM users WHERE current_room = %s", (room_name,))
    users = cursor.fetchall()

    formatted = f"{sender} > {msg}"
    for user in users:
        with lock:
            user_conn = userList.get(user[0])
        if user_conn:
            try:
                user_conn.send((formatted + "\n").encode())
            except:
                continue

def createRoom(conn, user_name):
    conn.send("Enter room name: ".encode())
    room_name = conn.recv(1024).decode().strip()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO rooms (room_name, created_by, created_at) VALUES (%s, %s, %s)", (room_name, user_name, created_at))
    myconn.commit()
    conn.send(f"Room '{room_name}' created.\n".encode())

def joinRoom(conn, user_name):
    cursor.execute("SELECT room_name FROM rooms")
    rooms = [row[0] for row in cursor.fetchall()]
    if not rooms:
        conn.send("No rooms available. Create one.\n".encode())
        return None

    conn.send("Available Rooms:\n".encode())
    for room in rooms:
        conn.send(f"{room}\n".encode())
    conn.send("Enter room name: ".encode())
    room_name = conn.recv(1024).decode().strip()

    if room_name in rooms:
        cursor.execute("UPDATE users SET current_room = %s WHERE user_name = %s", (room_name, user_name))
        myconn.commit()
        broadcast("System", f"{user_name} joined the room.", room_name)
        return room_name
    else:
        conn.send("Invalid room name.\n".encode())
        return None

def handleClient(conn, addr):
    user_name = None
    try:
        while True:
            conn.send("1. Login\n2. Signup\nChoice: ".encode())
            choice = conn.recv(1024).decode().strip()
            if choice == '1':
                conn.send("Enter username: ".encode())
                user_name = conn.recv(1024).decode().strip()
                cursor.execute("SELECT pass FROM users WHERE user_name = %s", (user_name,))
                result = cursor.fetchone()
                if result:
                    conn.send("Enter password: ".encode())
                    pw = conn.recv(1024).decode()
                    if hashed(pw) == result[0]:
                        conn.send("Login successful.\n".encode())
                        with lock:
                            userList[user_name] = conn
                        break
                    else:
                        conn.send("Wrong password.\n".encode())
                else:
                    conn.send("User not found.\n".encode())
            elif choice == '2':
                conn.send("Enter new username: ".encode())
                user_name = conn.recv(1024).decode().strip()
                cursor.execute("SELECT * FROM users WHERE user_name = %s", (user_name,))
                if cursor.fetchone():
                    conn.send("Username already exists.\n".encode())
                    continue
                conn.send("Enter password: ".encode())
                pw = conn.recv(1024).decode().strip()
                cursor.execute("INSERT INTO users (user_name, pass) VALUES (%s, %s)", (user_name, hashed(pw)))
                myconn.commit()
                conn.send("Signup successful.\n".encode())
                with lock:
                    userList[user_name] = conn
                break
            else:
                conn.send("Invalid choice.\n".encode())

        while True:
            conn.send("\n1. Create Room\n2. Join Room\nChoice: ".encode())
            option = conn.recv(1024).decode().strip()
            if option == '1':
                createRoom(conn, user_name)
            elif option == '2':
                room = joinRoom(conn, user_name)
                if room:
                    break
            else:
                conn.send("Invalid option.\n".encode())

        while True:
            conn.send("\n0. Exit\n1. Chat\n2. List Users\n3. Count Users\nChoice: ".encode())
            ch = conn.recv(1024).decode().strip()
            if ch == '1':
                conn.send("Type messages. Type '0' to stop.\n".encode())
                while True:
                    msg = conn.recv(1024).decode().strip()
                    if msg == '0':
                        break
                    broadcast(user_name, msg, room)
            elif ch == '2':
                cursor.execute("SELECT user_name FROM users WHERE current_room = %s", (room,))
                users = [row[0] for row in cursor.fetchall()]
                conn.send(("\n".join(users) + "\n").encode())
            elif ch == '3':
                cursor.execute("SELECT COUNT(*) FROM users WHERE current_room = %s", (room,))
                count = cursor.fetchone()[0]
                conn.send(f"Active users: {count}\n".encode())
            elif ch == '0':
                cursor.execute("UPDATE users SET current_room = NULL WHERE user_name = %s", (user_name,))
                myconn.commit()
                broadcast("System", f"{user_name} left the room.", room)
                break
            else:
                conn.send("Invalid choice.\n".encode())
    except:
        pass
    finally:
        conn.close()
        with lock:
            if user_name in userList:
                del userList[user_name]
        print(f"{user_name} disconnected.")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handleClient, args=(conn, addr)).start()
