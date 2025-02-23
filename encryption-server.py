import os
import socket
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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

class Asymmetric(Encrypt):
    def __init__(self):
        super().__init__()
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        
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

        print("RSA key pair generated successfully by server")

    def encode(self, message):
        self.message = self.public_key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                    )
                )

    def decode(self, data):
        self.message = self.private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                    )
                ).decode()

class Hybrid(Encrypt):
    def __init__(self):
        super().__init__()
        self.key_ready = False

        self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
                )
        self.public_key = self.private_key.public_key()

        with open("server_private_key.pem", "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
                ))

        with open("server_public_key.pem", "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo))

    def decrypt_key(self, encrypted_key):
        with open("server_private_key.pem", "rb") as f:
            self.private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        self.key_decrypted = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                    )
                )
        self.key_ready = True

    def encode(self, message):
        initialization_vector = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key_decrypted), models.CBC(initialization_vector))
        encryptor = cipher.encryptor()
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        cipher_text = encryptor.update(padded_data) + encryptor.finalize()

        self.message = initialization_vector + cipher_text

    def decode(self, message):
        initialization_vector = message[:16]
        ciphertext = message[16:]

        cipher = Cipher(algorithms.AES(self.key_decrypted), modes.CBC(initialization_vector))
        decryptor = cipher.decryptor()

        padded_message = decryptor.update(ciphertext) + decryptor.finalize()

        unpader = sym_padding.PKCS7(128).unpadder()
        self.message = unpader.update(padded_message) + unpadder.finalize()
        self.message = self.message.decode()


#open socket connection through TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(5)

clients = []

encryption = Hybrid()


def handle_client(conn, addr):
    print(f"Connection from {addr}")

    encrypted_key = conn.recv(256)
    encryption.decrypt_key(encrypted_key)

#send the encryption key to the client
    if type(encryption) == Symmetric: 
        conn.send(encryption.key)
    elif type(encryption) == Asymmetric:
        conn.send(encryption.public_bytes)
    #elif isinstance(encryption, Hybrid):
    #    encrypted_key = conn.recv(1024)
    #    encryption.decrypt(encrypted_key)

    while True:
        try:
            #allow user to type messages to send to the client
            data = conn.recv(1024)
            #allow user to exit the loop
            if not data:
                break
            encryption.decode(data)
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
    
    if isinstance(encryption, Hybrid):
        while not encryption.key_ready:
            pass

    while True:
        message = input("Server: ")
        encryption.encode(message)
        broadcast(encryption.message, None)

print("Server started. Waiting for connection...")

#encryption = Hybrid()
#if isinstance(encryption, Hybrid):
#    encrypted_key = conn.recv(1024)
#    encryption.decrypt(encrypted_key)

server_send_thread = threading.Thread(target=send_message)
server_send_thread.start()

#encryption = Symmetric()
#encryption = Asymmetric()
#encryption = Hybrid()


#close the connection and the server
while True:
    conn, addr = server.accept()
    
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
