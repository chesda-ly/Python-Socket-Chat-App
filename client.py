import socket
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Send an email notification
def send_email(receiver_email, subject, body):
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Start the client
def start():
    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        return

    username = input('Enter your username: ')
    email = input('Enter your email: ')  # NEW: Prompt for email
    connection = connect()

    # Send username and email to server
    send(connection, username)
    time.sleep(0.1)  # Small delay to ensure messages are sent in the right order
    send(connection, email)

    # Start a new thread to receive messages from the server
    threading.Thread(target=receive, args=(connection,)).start()

    print("""Welcome to the Chat Room!
- Messages will be broadcasted to all clients INCLUDING the server
- Notices sent by the server will be displayed as [SERVER]: message
- To send a private message, use @username message
- To send a private message to multiple users, use @username1,username2 message
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
