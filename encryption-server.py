import socket
import threading
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

#open socket connection through TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(1)

print("Server started. Waiting for connection...")
conn, addr = server.accept()
print(f"Connection from {addr}")

#send a message to the client
while True:
    try:
        #allow user to type messages to send to the client
        data = input("Enter a message to send (Type 'Exit' to quit): ")
        #allow user to exit the loop
        if data.lower() == "exit":
            break
        conn.sendall(data.encode())
    #error handling in case it does not work properly
    except Exception as e:
        print(f"Error occured here: {e}")
        break

#close the connection and the server
conn.close()
server.close()