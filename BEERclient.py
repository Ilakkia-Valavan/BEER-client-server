import sys
import socket
import threading

class Client:
    def __init__(self,HOST,PORT):
        
        self.name= input("enter ur name: ")
        self.ID= input("enter ur ID: ")
        self.role= input("Enter your role (p = Player, s = Spectator): ").lower().strip()
        
        self.client={
                'client_name': self.name,
                'client_ID': self.ID,
                'client_role': self.role
                }
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        print(f"[CONNECTED] Connected to server at {HOST}:{PORT}")
        
        
        self.talk_to_server()
        
    def talk_to_server(self):
        # Send the information to the server
        self.socket.send(str(self.client).encode())
        
        threading.Thread(target= self.receive_messages).start()


    def receive_messages(self):
        while True:
            server_message= self.socket.recv(1024).decode()
            if not server_message.strip():
                sys.exit()
            #adds colour
            print("\033[1;31;40m"+ server_message+ "\033[0m")


if __name__ == '__main__':
    Client('127.0.0.1',7632)
