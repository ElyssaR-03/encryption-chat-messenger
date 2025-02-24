#code written by Elyssa Ratliff
import socket
import threading
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import scrolledtext
 
def receive_messages():
    #receive the message from the server
    while True:
        try:
            #allows client to receive messages sent
            data = client.recv(1024)
            if not data:
                break
            decrypted_message = cipher_suite.decrypt(data).decode()

            #allows for the decrypted messages to be displayed in the chat window
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, decrypted_message + '\n')
            chat_area.config(state=tk.DISABLED)
        #error handling in case it does not work properly
        except Exception as e:
            print(f"Error occured here {e}")
            break
    client.close

def send_message():

    #if clients types exit the chat and connection will close
    message = message_entry.get()
    if message.lower() == 'exit':
        client.close()
        root.quit()

    #otherwise, continue to encrypt and send messages back and forth
    else:            
        full_message = f"{nickname}: {message}"
        encrypted_message = cipher_suite.encrypt(full_message.encode())
        client.send(encrypted_message)

        chat_area.config(state=tk.NORMAL)
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, full_message + '\n')
        chat_area.config(state=tk.DISABLED)
        message_entry.delete(0, tk.END)

try:
    #open socket connection through TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 12345))

    #receive the encryption key from the server
    key = client.recv(1024)
    cipher_suite = Fernet(key)

    #prompts client to input a nickname
    nickname = input("Enter nickname: ")

    #start threading for receiving messages
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    #create a GUI for the client
    root = tk.Tk()
    root.title("Chat Client")   

    #creates the chat window where the messages can be seen
    chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    chat_area.pack(padx=10, pady=10)
    
    #allows the client to type messages to send to the server and display in window
    message_entry = tk.Entry(root)
    message_entry.pack(padx=10, pady=10)

    #allows user to send their message to server to be displayed 
    send_button  = tk.Button(root, text="Send", command=send_message)
    send_button.pack()
    
    #when client close the messaging, the window will close 
    root.protocol("WM_DELETE_WINDOW", client.close)
    root.mainloop()

#client error handling
except Exception as e:
    print(f"Client error: {e}")
