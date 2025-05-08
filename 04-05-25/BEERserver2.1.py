import ast
import socket
import threading
import json
import random
import signal
import sys
import time
from ServerMessageUtil import ServerMessageUtil
from battleship import Board, parse_coordinate, SHIPS
from Utility import Util

class Server:
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        self.game_in_progress = False 
        self.message_util = ServerMessageUtil()

        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        self.players = []    # Max 2
        self.lobby = []      # Waiting players
        self.spectators = [] # Spectators
        threading.Thread(target=self.manage_player).start() #will run in background

   
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    def listen(self):

        try:
            while True:
                client_socket, address = self.socket.accept()
                print("Connection from: " + str(address))

                try:
                    client_message = ast.literal_eval(client_socket.recv(1024).decode())
                    client_detail = client_message["data"]
                    print(client_message)
                    client_detail["client_socket"]=client_socket
                    #print("hi")


                    role = client_detail["client_role"].upper() 

                    if role == 'P':
                        self.player_registration(client_detail) 
                        
                        
                    elif role == 's':  
                        # Spectator
                        self.spectators.append(client_detail)
                        client_socket.sendall("You have choses spectator.\n".encode())
                        threading.Thread(target=self.handle_new_spectator, args=(client_detail,)).start()

                except Exception as error:
                    print("An error occurred:", error) # An error occurred: name 'x' is not defined
                    continue
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Perform cleanup actions (e.g., closing connections)
            sys.exit(0) 




    def handle_new_spectator(self, spectator):
        client_name = spectator['client_name']
        client_socket = spectator['client_socket']

        while True:
            try:
                client_message = client_socket.recv(1024).decode()
                #handles peple who are not players and not in waiting list but only wish to spectate
                
            except:
                break





    def manage_player(self):
        """
        Manages the lobby and starts a game if at least 2 players are waiting.
        - If a game is already in progress, sleep and retry later.
        - If not, start a new game with the first two players in the lobby.
        - Players remaining in the lobby are notified of their queue position.
        - If fewer than 2 players, notify the player(s) to wait for opponent.
        """
        notify_interval = 0
        print("manage_player 1")
        try:
            while True:
                
                notify_interval += 1
                time.sleep(1)
                
                if len(self.lobby) >= 2 and not self.game_in_progress:
                    # Start new game
                    self.game_in_progress = True
                    player1 = self.lobby.pop(0)
                    player2 = self.lobby.pop(0)

                    print(f"Starting game between {player1['client_name']} and {player2['client_name']}.")
                    threading.Thread(target=self.handle_game, args=(player1, player2)).start()
                
                if notify_interval == 60:
                    notify_interval = 0 #to-do clean up
                    for i, waiting_player in enumerate(self.lobby): 
                        message = self.message_util.get_queue_wait_message(i, len(self.lobby))
                        try:
                            waiting_player["client_socket"].sendall(str(message).encode())
                        except:
                            print(f"Failed to notify {waiting_player['client_name']} in lobby.")
    
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Perform cleanup actions (e.g., closing connections)
            sys.exit(0)
                
                        

    def handle_game(self, player1, player2):
        print(f"Match started between {player1['client_name']} and {player2['client_name']}")

        try:
            # Initiate match intro
            player1["board"] = Board()
            ships = SHIPS
            print("ships: ",ships)
            player2["board"] = Board()
            
            player1['client_socket'].send(str(Util.get_info_message("Match started! You are Player 1.\n")).encode())
            player2['client_socket'].send(str(Util.get_info_message("Match started! You are Player 2.\n")).encode())
            player1["client_socket"].send(str(self.message_util.get_place_ship_message(ships)).encode())

        except Exception as e:
            print(f"[ERROR] {e}")


    def player_registration(self, client_detail):
        add_to_lobby = True
        for player in self.lobby:
            if player["client_ID"] != client_detail["client_ID"]:
                continue
            if player["client_ID"] == client_detail["client_ID"] and player["client_name"] != client_detail["client_name"]:
                add_to_lobby = False
                break

            elif player["client_ID"] == client_detail["client_ID"] and player["client_name"] == client_detail["client_name"] and client_detail["session_id"] != None and player["session_id"] == client_detail["session_id"]:
                client_detail["client_socket"].sendall("re-joined in waiting lobby".encode())
                #to-do: check if earlier socket is active for secuirty
                #to-do: rejoin implementation
                player["client_socket"] = client_detail["client_socket"] 
                add_to_lobby = False
                break
          
        if add_to_lobby:
            #to-do add session id to client_detail
            client_detail["session_id"] = self.generate_sessionID()
            self.lobby.append(client_detail)

            #formatted error response here
            registration_response = self.message_util.get_registration_response(client_detail,"SUCCESS")
            client_detail["client_socket"].sendall(str(registration_response).encode())

        else:
            #formatted error response here
            registration_response= self.message_util.get_registration_response(client_detail,"FAIL","DUP001","user ID exists")
            client_detail["client_socket"].sendall(str(registration_response).encode())

               
    def generate_sessionID(self):
        print("generate session id 1")
        random_num = random.randint(1,1000)
        return random_num
                
                    

if __name__ == '__main__':
    server = Server('127.0.0.1', 7632)
    server.listen()




 