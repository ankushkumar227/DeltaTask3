from datetime import datetime
import socket
import threading
import mysql.connector

# MySQL connection
myconn = mysql.connector.connect(
    host='localhost',
    user='Ankush',
    password='Elon@2005',
    database='chatServer'
)
cursor = myconn.cursor()

# Socket setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost', 5050))
server.listen()
print("Server started...")

userList = {}  # {username: conn}


def broadcast(conn, sender, msg, room_name):
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_history (room_name, sent_by, msg, sent_at)
        VALUES (%s, %s, %s, %s)
    """, (room_name, sender, msg, sent_at))
    myconn.commit()

    cursor.execute("SELECT user_name FROM users WHERE current_room = %s", (room_name,))
    rows = cursor.fetchall()

    formatted = f"{sender} > {msg}"
    for user in rows:
        user_conn = userList.get(user[0])
        if user_conn and user_conn != conn:
            try:
                user_conn.send(formatted.encode())
            except:
                pass  # Avoid crashing if one client is unreachable


def createRoom(conn, user_name):
    conn.send("Enter room name: ".encode())
    room_name = conn.recv(1024).decode().strip()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO rooms (room_name, created_by, created_at)
        VALUES (%s, %s, %s)
    """, (room_name, user_name, created_at))
    myconn.commit()
    conn.send(f"Room '{room_name}' created.\n".encode())


def joinRoom(conn, user_name):
    cursor.execute("SELECT room_name FROM rooms")
    rows = cursor.fetchall()
    rooms = [row[0] for row in rows]

    if not rooms:
        conn.send('No rooms available. Please create one.\n'.encode())
        return None

    conn.send('\nAvailable Rooms:\n'.encode())
    for room in rooms:
        conn.send(f"{room}\n".encode())

    conn.send('Enter room name: '.encode())
    room_name = conn.recv(1024).decode().strip()

    if room_name in rooms:
        cursor.execute("""
            UPDATE users SET current_room = %s WHERE user_name = %s
        """, (room_name, user_name))
        myconn.commit()

        broadcast(conn, "System", f"{user_name} joined the room.", room_name)
        return room_name
    else:
        conn.send("Invalid room name.\n".encode())
        return None


def leaveRoom(conn, user_name, room_name):
    cursor.execute("UPDATE users SET current_room = NULL WHERE user_name = %s", (user_name,))
    myconn.commit()
    broadcast(conn, "System", f"{user_name} left the room.", room_name)


def handleClient(conn, addr, user_name):
    conn.send(f"\nWelcome {user_name}!\n".encode())
    room_name = None

    while True:
        conn.send('\n--- Menu ---\n1. Create Room\n2. Join Room\nChoice: '.encode())
        choice = conn.recv(1024).decode().strip()
        if choice == '1':
            createRoom(conn, user_name)
        elif choice == '2':
            room_name = joinRoom(conn, user_name)
            if room_name:
                break
        else:
            conn.send('Invalid choice.\n'.encode())

    # Inside room
    while room_name:
        conn.send('\n0. Exit\n1. Chat\n2. List Users\n3. Count Users\nChoice: '.encode())
        choice = conn.recv(1024).decode().strip()

        if choice == '1':
            while True:
                msg = conn.recv(1024).decode().strip()
                if msg == '0' or not msg:
                    break
                broadcast(conn, user_name, msg, room_name)

        elif choice == '0':
            leaveRoom(conn, user_name, room_name)
            break

        elif choice == '2':
            cursor.execute("SELECT user_name FROM users WHERE current_room = %s", (room_name,))
            users = cursor.fetchall()
            user_list = '\n'.join(user[0] for user in users)
            conn.send(user_list.encode())

        elif choice == '3':
            cursor.execute("SELECT COUNT(*) FROM users WHERE current_room = %s", (room_name,))
            count = cursor.fetchone()[0]
            conn.send(f"Active users: {count}\n".encode())

        else:
            conn.send("Invalid choice.\n".encode())

    # Cleanup
    cursor.execute("UPDATE users SET current_room = NULL WHERE user_name = %s", (user_name,))
    myconn.commit()
    conn.close()
    del userList[user_name]
    print(f"{user_name} disconnected.")


# Main Server Loop
while True:
    try:
        conn, addr = server.accept()

        cursor.execute("SELECT user_name FROM users")
        all_users = [row[0] for row in cursor.fetchall()]

        while True:
            conn.send("1. Log in\n2. Sign up\nChoice: ".encode())
            choice = conn.recv(1024).decode().strip()

            if choice == '1':
                conn.send("Enter Username: ".encode())
                user_name = conn.recv(1024).decode().strip()
                if user_name in all_users:
                    conn.send("Successfully Logged in.\n".encode())
                    userList[user_name] = conn
                    break
                else:
                    conn.send("User not found.\n".encode())

            elif choice == '2':
                conn.send("Enter Username: ".encode())
                user_name = conn.recv(1024).decode().strip()
                if user_name not in all_users:
                    cursor.execute("INSERT INTO users (user_name, current_room) VALUES (%s, NULL)", (user_name,))
                    myconn.commit()
                    conn.send("User successfully created.\n".encode())
                    userList[user_name] = conn
                    break
                else:
                    conn.send("Username already taken.\n".encode())

            else:
                conn.send("Wrong Choice.\n".encode())

        # Start client thread
        threading.Thread(target=handleClient, args=(conn, addr, user_name)).start()

    except Exception as e:
        print("Server error:", e)
        break
