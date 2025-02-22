import socket
import threading
from cryptography.fernet import Fernet

#symmetric_encryption = True

#def symmetric_encryption():
    
 #   global key, cipher_suite
    
 #   key = Fernet.generate_key()
 #   cipher_suite = Fernet(key)

class Encrypt:
    def __init__(self):
        self.encrypt = True

class Symmetric(Encrypt):
    def __init__(self):
        super().__init__()
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def encode(self, message):
        self.message = self.cipher_suite.encrypt(message.encode())
    def decode(self, data):
        self.message = self.cipher_suite.decrypt(data).decode()

#open socket connection through TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(5)

clients = []

#if symmetric_encryption:
#    symmetric_encryption()

def handle_client(conn, addr):
    print(f"Connection from {addr}")

    #send the encryption key to the client
    conn.send(encryption.key)
    while True:
        try:
            #allow user to type messages to send to the client
            data = conn.recv(1024)
            #allow user to exit the loop
            if not data:
                break
            encryption.decode(data)
            #decrypted_message = cipher_suite.decrypt(data).decode()
            print(f"Received from {addr}: {encryption.message}")
            broadcast(data, conn)
        #error handling in case it does not work properly
        except Exception as e:
            print(f"Error occured here: {e}")
            break
    conn.close()
def broadcast(message, connection):
    for client in clients:
        if client != connection:
            try:
                client.send(encryption.message)
            except Exception as e:
                print(f"Error sending message: {e}")
                client.close()
                clients.remove(client)

def send_message():
    while True:
        message = input("Server: ")
        encryption.encode(message)
        #encrypted_message = cipher_suite.encrypt(message.encode())
        broadcast(encryption.message, None)

print("Server started. Waiting for connection...")

server_send_thread = threading.Thread(target=send_message)
server_send_thread.start()

encryption = Symmetric()

#close the connection and the server
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
