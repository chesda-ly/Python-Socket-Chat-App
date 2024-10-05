import threading
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_email = "email@gmail.com"
smtp_password = "your_password"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
usernames = {}
emails = {}
clients_lock = threading.Lock()

def send_email_notification(sender, sender_address, receiver, receiver_address, message):
    subject = f"New message from {sender}"
    body = f"""
    Greetings {receiver},

    You have received a new message from {sender} ({sender_address}):
    "{message}"

    Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    -- Server Notification --
    """

    email_message = MIMEMultipart()
    email_message["From"] = smtp_email
    email_message["To"] = receiver_address
    email_message["Subject"] = subject
    email_message.attach(MIMEText(body, "plain"))

    try:
        smtp_server = smtplib.SMTP(smtp_host, smtp_port)
        smtp_server.starttls()
        smtp_server.login(smtp_email, smtp_password)
        smtp_server.sendmail(smtp_email, receiver_address, email_message.as_string())
        smtp_server.quit()
        print(f"[EMAIL SENT] {receiver_address}")
    except Exception as e:
        print(f"[EMAIL FAILED] Email was not sent. Error: {e}")

# Broadcast messages to all clients
def broadcast(message, sender_client, receiver=None):
    with clients_lock:
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

def handle_client(client, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    try:
        username = client.recv(1024).decode(FORMAT)
        email = client.recv(1024).decode(FORMAT)
        with clients_lock:
            clients.append(client)
            usernames[client] = username
            emails[client] = email

        print(f"[NEW CONNECTION] {username} (Email: {email}) connected.")

        while connected:
            try:
                msg = client.recv(1024)
                if msg == DISCONNECT_MESSAGE.encode(FORMAT):
                    print(f"[DISCONNECT] {usernames[client]} disconnected.")
                    broadcast(f"[SERVER]: {usernames[client]} has left the chat.".encode(FORMAT), client)
                    client.close()
                    with clients_lock:
                        clients.remove(client)
                    break

                elif msg.startswith(b"@"):
                    receivers, private_msg = msg[1:].decode(FORMAT).split(" ", 1)
                    recipients = receivers.split(",")
                    private_msg = f"{usernames[client]} [PRIVATE] - {private_msg}".encode(FORMAT)
                    for receiver in recipients:
                        broadcast(private_msg, client, receiver.strip())

                elif msg:
                    msg_text = f"{usernames[client]}: {msg.decode(FORMAT)}"
                    print(f"[MESSAGE RECEIVED] {msg_text}")
                    broadcast(msg_text.encode(FORMAT), client)

                    # Send email notification
                    for c in clients:
                        if c != client:
                            send_email_notification(usernames[client], emails[client], usernames[c], emails[c], msg.decode(FORMAT))

                else:
                    break

            except Exception as e:
                print(f"[ERROR] {e}")
                with clients_lock:
                    if client in clients:
                        clients.remove(client)
                client.close()
                break

    finally:
        with clients_lock:
            if client in clients:
                clients.remove(client)
            if client in usernames:
                del usernames[client]
            if client in emails:
                del emails[client]

def start():
    print('[SERVER STARTED]!')
    server.listen()
    threading.Thread(target=announce).start()
    while True:
        try:
            client, addr = server.accept()
            print(f"[NEW CONNECTION] {addr} connected.")
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except Exception as e:
            print(f"[ERROR] {e}")
            break

print("[STARTING] Server is starting...")
start()