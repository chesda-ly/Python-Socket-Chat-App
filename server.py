import threading
import socket

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
usernames = {}

# Broadcast messages to all clients
def broadcast(message, sender_client, receiver=None):
    if receiver:
        for client, username in usernames.items():
            if username == receiver:
                try:
                    client.send(message)
                    
                except:
                    client.close()
                    
                return
    else:
        for client in clients:
            if client != sender_client:
                try:
                    client.send(message)
                    
                except:
                    client.close()
        
# Announce messages to all clients             
def announce():
    while True:
        msg = input()
        if msg == "q":
            print("Server is closed.")
            server.close()
            break
        
        else:
            formatted_msg = f"[SERVER]: {msg}".encode(FORMAT)
            broadcast(formatted_msg, None)
                
def handle_client(client):
    username = client.recv(1024).decode(FORMAT)
    usernames[client] = username
    print(f"[NEW CONNECTION] {username} connected.")
    broadcast(f"[SERVER]: {username} has joined the chat!".encode(FORMAT), client)    

    while True:
        try:
            msg = client.recv(1024)
            if msg == DISCONNECT_MESSAGE.encode(FORMAT):
                print(f"[DISCONNECT] {usernames[client]} disconnected.")
                broadcast(f"[SERVER]: {usernames[client]} has left the chat.".encode(FORMAT), client)
                client.close()
                clients.remove(client)
                break
            
            elif msg.startswith(b"@"):
                receivers, private_msg = msg[1:].decode(FORMAT).split(" ", 1)
                recipients = receivers.split(",")
                private_msg = f"{usernames[client]} [PRIVATE] - {private_msg}".encode(FORMAT)
                for receiver in recipients:
                    broadcast(private_msg, client, receiver.strip())
                
            elif msg:
                msg = f"{usernames[client]}: {msg.decode(FORMAT)}".encode(FORMAT)
                print(f"[MESSAGE RECEIVED] {msg.decode(FORMAT)}")
                broadcast(msg, client)
                
            else:
                break
            
        except:
            clients.remove(client)
            client.close()
            break

def start():
    print('[SERVER STARTED]!')
    server.listen()
    threading.Thread(target=announce).start()
    while True:
        try:
            client, addr = server.accept()
            print(f"[NEW CONNECTION] {addr} connected.")
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            
        except:
            break

print("[STARTING] Server is starting...")
start()
