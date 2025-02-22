import socket
import threading
from cryptography.fernet import Fernet


class Encrypt:
    def __init__(self):
        self.encrypt = True

class Symmetric(Encrypt):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.cipher_suite = Fernet(key)


    def encode(self, message):
        self.message = self.cipher_suite.encrypt(message.encode())

    def decode(self, data):
        self.message = self.cipher_suite.decrypt(data).decode()

class Asymmetric(Encrypt):
    def __init__(self, key):
        self.public_key = serialization.load_pem_public_key(key)
        
        with open("server_private_key.pem", "rb"), f:
            self.private_key = serialization.load_pem_private_key(f.read(), password=None)
        
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
                )

def receive_messages():
    #receive the message from the server
    while True:
        try:
            #allows client to receive messages sent
            data = client.recv(1024)
            if not data:
                break
            encryption.decode(data)
            print(f"Received: {encryption.message}")
        #error handling in case it does not work properly
        except Exception as e:
            print(f"Error occured here {e}")
            break
    client.close

def send_message():
    while True:
        message = input("Client: ")
        if message.lower() == 'exit':
            client.close()
            break
        encryption.encode(message)
        client.send(encryption.message)


try:
    #open socket connection through TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 12345))

    key = client.recv(1024)

    #encryption = Symmetric(key)
    encryption = Asymmetric(key)

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    send_thread = threading.Thread(target=send_message)
    send_thread.start()

#client error handling
except Exception as e:
    print(f"Client error: {e}")
