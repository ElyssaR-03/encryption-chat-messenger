import os
import socket
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import time

#class implementation by karla robles
#this section aims to encapsulate the symmetric and asymmetric encryption classes into a
#single class such that they may be called with the same function calls elsewhere
#with the aim of enhancing code readability
class Encrypt:
    def __init__(self):
        self.encrypt = True
        self.time_to_encode = []
        self.time_to_decode = []


class Symmetric(Encrypt):
    def __init__(self):
        super().__init__()

        print("Initializing symmetric encryption class")

        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

        print("Key and cipher suite generated")

    def encode(self, message):

        print("Symmetric encryption encoding message...")
        print(f"Message: {message}")
        
        time_start = time.perf_counter()

        self.message = self.cipher_suite.encrypt(message.encode())
    
        time_end = time.perf_counter()

        encoding_time = time_end - time_start

        print(f"Encoded message: {self.message}")
        print(f"Encoding took: {encoding_time} seconds") 


        self.time_to_encode.append(encoding_time)


    def decode(self, data):

        print("Symmetric encryption decoding message...")
        print(f"Message: {data}")

        time_start = time.perf_counter()

        self.message = self.cipher_suite.decrypt(data).decode()

        time_end = time.perf_counter()

        decoding_time = time_end - time_start

        print(f"Decoded message: {self.message}")
        print(f"Decoding took: {decoding_time} seconds")

        self.time_to_decode.append(decoding_time)


class Asymmetric(Encrypt):
    def __init__(self):
        super().__init__()

        print("Initializing asymmetric encryption class")

        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        
        print("RSA private key generated")
        print("Public key generated")

        self.private_bytes = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())

        self.public_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)

        with open("server_private_key.pem", "wb") as f:
            f.write(self.private_bytes)

        with open("server_public_key.pem", "wb") as f:
            f.write(self.public_bytes)

        print("Private and public keys generated and writted to pem files")


    def encode(self, message):
        print("Asymmetric encryption encoding message...")
        print(f"Message: {message}")

        time_start = time.perf_counter()

        self.message = self.public_key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                    )
                )
        time_end = time.perf_counter()

        encoding_time = time_end - time_start

        print(f"Encoded message: {self.message}")
        print(f"Encoding took: {encoding_time} seconds")

        self.time_to_encode.append(encoding_time)

    def decode(self, data):

        print("Asymmetric encryption decoding message...")
        print(f"Message: {data}")

        time_start = time.perf_counter()

        self.message = self.private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                    )
                ).decode()

        time_end = time.perf_counter()
        
        decoding_time = time_end - time_start

        print(f"Decoded message: {self.message}")
        print(f"Decoding took: {decoding_time} seconds")

        self.time_to_decode.append(decoding_time)

#open socket connection through TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(5)

clients = []

encryption_symmetric = Symmetric()
encryption_asymmetric = Asymmetric()


def handle_client(conn, addr):
    
    print(f"Connection from {addr}")

#    print("Server sent symmetric key to client")
#    conn.send(encryption_symmetric.key)

    print("Server sent asymmetric bytes to client")
    conn.send(encryption_asymmetric.public_bytes)

    while True:
        try:
            #allow user to type messages to send to the client
            data = conn.recv(1024)
            #allow user to exit the loop
            if not data:
                break
#            encryption_symmetric.decode(data)
            encryption_asymmetric.decode(data)
#            print(f"Received from {addr}: {encryption_symmetric.message}")
            print(f"Received from {addr}: {encryption_asymmetric.message}")
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
#                client.send(encryption_symmetric.message)
                client.send(encryption_asymmetric.message)
            except Exception as e:
                print(f"Error sending message: {e}")
                client.close()
                clients.remove(client)

def send_message():
    
    while True:
        message = input("Server: ")
        encryption_symmetric.encode(message)
        encryption_asymmetric.encode(message)
        
#        broadcast(encryption_symmetric.message, None)
        broadcast(encryption_asymmetric.message, None)

print("Server started. Waiting for connection...")


server_send_thread = threading.Thread(target=send_message)
server_send_thread.start()


#close the connection and the server
while True:
    conn, addr = server.accept()
    
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
