import socket
import threading
import tkinter as tk    

try:
    #open socket connection through TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 12345))

#receive the message from the server
    while True:
        try:
            #allows client to receive messages sent
            data = (client.recv(1024)).decode()
            if not data:
                break
            print(f"Received: {data}")
        #error handling in case it does not work properly
        except Exception as e:
            print(f"Error occured here {e}")
            break

    #close the connection
    client.close()
#client error handling
except Exception as e:
    print(f"Client error: {e}")

class send_message(threading.Thread):
    def __init__(self, s):
        threading.Thread.__init__(self)
        self.s = s
    def run(self):
        while True:
            message = input()
            self.s.send(message.encode())