import socket
import time
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# Connect to the server
def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

# Send a message to the server
def send(client, msg, receiver=None):
    if receiver:
        message = f"@{receiver} {msg}".encode(FORMAT)
        
    else:
        message = msg.encode(FORMAT)
        
    client.send(message)

# Receive messages from the server
def receive(client):
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                print(msg)
                
            else:
                break
            
        except:
            client.close()
            break

def start():
    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        return

    username = input('Enter your username: ')
    connection = connect()
    
    # Send username to server
    send(connection, username)
    
    # Start a new thread to receive messages from the server
    threading.Thread(target=receive, args=(connection,)).start()
    
    print("""Welcome to the Chat Room!
- Messages will be broadcated to all clients INCLUDING ther server
- Notices sent by the server will be displayed as [SERVER]: message
- To send a private message, use @username message
- To send a private message to multiople users, use @username1,username2 message
- To disconnect, type 'q'
Have Fun!
----------------------------------------""")
    while True:
        msg = input()

        if msg == 'q':
            break
        
        if msg.startswith('@'):
            try:
                receiver, private_msg = msg[1:].split(' ', 1)
                send(connection, private_msg, receiver)
            except ValueError:
                print('Invalid format. Please use @username message')
        else:
            send(connection, msg)

    send(connection, DISCONNECT_MESSAGE)
    time.sleep(1)
    print('Disconnected')
    connection.close()


start()
