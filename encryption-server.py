import socket
import threading #import threading for message sending and keeping track
from cryptography.fernet import Fernet

#generates encryption ket for client when sending messages
key = Fernet.generate_key()
cipher_suite = Fernet(key)

#open socket connection through TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(5)

clients = []

#extabslished connection to client for message sending
def handle_client(conn, addr):
    print(f"Connection from {addr}")

    #send the encryption key to the client
    conn.send(key)
    while True:
        try:
            #allow server to receive encryped messages from client
            data = conn.recv(1024)
            #allow user to exit the loop
            if not data:
                break
            #decrypes messages upon receiving
            decrypted_message = cipher_suite.decrypt(data).decode()
            print(f"Received from {addr}: {decrypted_message}")
            broadcast(data, conn)
        #error handling in case it does not work properly
        except Exception as e:
            print(f"Error occured here: {e}")
            break
    #closes the connection when messing is done
    conn.close()
#broadcasts connection to 
def broadcast(message, connection):
    for client in clients:
        if client != connection:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                client.close()
                clients.remove(client)

print("Server started. Waiting for connection...")

#close the connection and the server
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()