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
from ServerHandler import ServerHandler
from PlayerServerHandler import PlayerServerHandler
import traceback

class Server:
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        self.game_in_progress = False 
        self.message_util = ServerMessageUtil()

        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        self.players = []    # Max 2
        self.player1 = None
        self.player2 = None
        self.game_log = []
        self.lobby = []      # Waiting players
        self.spectators = [] # Spectators
        self.message_queue=[]
        threading.Thread(target=self.manage_lobby).start() #will run in background
        threading.Thread(target=self.manage_spectator).start()

    def listen(self):

        try:
            while True:
                client_socket, address = self.socket.accept()
                #need to work on it
                
                print("Connection from: " + str(address))

                try:
                    threading.Thread(target=self.client_handler, args=(client_socket,)).start()
 
                    #role = client_detail["client_role"].upper() 
                except Exception as error:
                    print("An error occurred:", error) # An error occurred: name 'x' is not defined
                    continue

        except KeyboardInterrupt:
            print("Server shutting down...")
            # Perform cleanup actions (e.g., closing connections)
            sys.exit(0)

    def client_handler(self,client_socket):
        client_detail = {}

        while True:

            try:
                client_message = ast.literal_eval(client_socket.recv(1024).decode())

                if client_message["command"] == "REGISTER" : 
                    client_detail = client_message["data"]

                    client_detail["client_socket"] = client_socket
                    role = client_detail["client_role"].upper() 

                    if role == 'P':
                        if client_detail["session_id"] == None or client_detail["session_id"] == "":
                            if self.player_registration(client_detail):
                                break
                        else: 
                            if self.player_rejoin(client_detail) :
                                break
                    elif role == "S":
                        self.spectator_registration(client_detail)
                        break

            except Exception as e:
                print("client handler error:" ,e)

    def spectator_registration(self, client_detail):
        self.spectators.append(client_detail)
        #client_detail["client_socket"].sendall(str(Util.get_info_message("Succesfully registered as Spectator")).encode())
        #time.sleep(1)
        threading.Thread(target=self.spectator_chat_handler, args=(client_detail,)).start()

    def manage_spectator(self):  
        local_message_queue = []
        local_game_log=[]
        while True:
            local_message_queue = []
            try:                
                if self.player1 and self.player2:
                    player1_grid = self.player1["handler"].get_hidden_grid()
                    player2_grid = self.player2["handler"].get_hidden_grid()

                    i = 0
                    while len(self.spectators) > 0:
                        spectator = self.spectators[i]
                        try:

                            spectator["client_socket"].sendall(
                                str(Util.get_grid_message_spectators(
                                    f"{self.player1['client_name']}'s board status", player1_grid,
                                    f"{self.player2['client_name']}'s board status", player2_grid
                                )).encode()
                            )
                        except Exception as e:
                            print("error popping spectator in board loop :", e)
                            a = self.spectators.pop(i)
                            print(f"removing spectator {a["client_name"]} from queue")
                            continue
                        
                        i+=1
                        if i >= len(self.spectators):
                            break

                i = 0
                print("manage spectator self message queue:", self.message_queue)

                while len(self.message_queue) > 0:
                    i+=1
                    print("in local message queue")
                    local_message_queue.append(self.message_queue.pop())
                    if i == 5:
                        break

                print("local message queue: ",local_message_queue)
                if len(local_message_queue) > 0:
                    
                    i = 0
                    while len(self.spectators) > 0:
                        spectator = self.spectators[i]
                        try:
                            spectator["client_socket"].sendall(str(self.message_util.send_chat_list(local_message_queue)).encode())
                        except Exception as e:
                            print("popping spectator in chat loop :", e)                           
                            a = self.spectators.pop(self.spectators.index(spectator))
                            print(f"removing spectator {a["client_name"]} from queue")

                            if i < len(self.spectators):
                                continue
                        
                        i+=1
                        if i >= len(self.spectators):
                            break

                            
                

            except Exception as e:
                traceback.print_exc()
                print(f"[ERROR] {e}.")

            time.sleep(30)

    def spectator_chat_handler(self, spectator):
        try:
            spectator_socket = spectator["client_socket"]
            spectator_name = spectator["client_name"]

            if self.game_in_progress :
                spectator_socket.sendall(
                    str(Util.get_info_message("Game in progress currently. You can chat with other spectators.")).encode()
                )
            else:
                spectator_socket.sendall(
                    str(Util.get_info_message("No game in progress currently. You can send chat with other spectators until new game starts")).encode()
                )

            while True:
                try:
                    raw = spectator_socket.recv(1024).decode().strip()
                    if not raw:
                        continue

                    client_message = ast.literal_eval(raw)

                    print("client message chat ",client_message)

                    if client_message["message_type"] == "CHAT":
                        chat_message = client_message["data"]["message"]
                        sender_name = client_message["data"]["name"]

                        #print(f"[CHAT] {sender_name}: {chat_message}")
                        print("send_chat_message format: ",self.message_util.send_chat_message(chat_message, sender_name))

                        self.message_queue.append(str(self.message_util.send_chat_message(chat_message, sender_name)))

                        print("message_queue ",self.message_queue)

                        # Broadcast to all spectators
                        """
                        for other in self.spectators:
                            try:
                                other["client_socket"].sendall(
                                    str(self.message_util.send_chat_message(chat_message, spectator)).encode()
                                )
                            except Exception as e:
                                print("error in broadcast chat ",e)
                                continue
                        """
                except Exception as e:
                    print(f"[CHAT RECEIVE ERROR] {e}")
                    break

        except Exception as e:
            print(f"[CHAT ERROR] {e}")




    def game_handler(self, player1, player2):

        player1_server_handler = PlayerServerHandler(player1)
        player2_server_handler = PlayerServerHandler(player2)
        
        self.player1["handler"] = player1_server_handler
        self.player2["handler"] = player2_server_handler

        player1['client_socket'].send(str(Util.get_info_message(f"Match started! You are playing with {player2["client_name"]}.\n")).encode())
        player2['client_socket'].send(str(Util.get_info_message(f"Match started! You are Player 2. Wait for {player1["client_name"]} to place ships\n")).encode())

        player1_server_handler.place_ship()
        player2_server_handler.place_ship()

        current_player = player1
        game_over = False

        while True:
            if not game_over:
                current_player['client_socket'].send(str(self.message_util.get_fire_request()).encode())
            else:
                break

            try:
                try:
                    current_player["client_socket"].settimeout(32)

                    client_message = ast.literal_eval(current_player["client_socket"].recv(1024).decode())
                    print("game handller() client msg: ", client_message)
                    print("game handller() current client : ", current_player)

                except socket.timeout as te:
                    print("in socket timeout exception")
                    client_message = self.message_util.get_fire_command_for_server_timeout(current_player, None)
                    current_player["timeout_count"] += 1

                    print("TIME OUT COUNT :" , current_player["timeout_count"])
                    print("time out error in game_handler(): ",te)                    
                    
                except Exception as e:
                    print("game handler timeout exception : ",e)

                
                if current_player["session_id"] == player1["session_id"]:
                    result, sunk_name, display_grid , return_message = player2_server_handler.fire_at(client_message)

                    self.game_log.append(Util.get_game_log_message(current_player,result,sunk_name, return_message))

                    player2_grid = player2_server_handler.get_hidden_grid() 

                    player2["client_socket"].send(str(Util.get_info_message_grid("Your board status", player2_grid)).encode())
                    current_player['client_socket'].send(str(Util.get_info_message_grid(return_message, display_grid)).encode()) 

                    if player2_server_handler.is_game_over():
                        game_over = True
                        threading.Thread(target=self.want_to_continue, args=(player1,True)).start()
                        threading.Thread(target=self.want_to_continue, args=(player2,False)).start()
                        
                elif current_player["session_id"] == player2["session_id"]:
                    result, sunk_name, display_grid, return_message = player1_server_handler.fire_at(client_message)
                    player1_grid = player1_server_handler.get_hidden_grid() 

                    player1["client_socket"].send(str(Util.get_info_message_grid("Your board status", player1_grid)).encode())
                    current_player['client_socket'].send(str(Util.get_info_message_grid(return_message, display_grid)).encode()) 

                    if player1_server_handler.is_game_over():         
                        game_over = True
                        threading.Thread(target=self.want_to_continue, args=(player1,False)).start()
                        threading.Thread(target=self.want_to_continue, args=(player2,True)).start()

                else:
                    print("session id not matching with both players")

                if current_player["session_id"] != player1["session_id"]:
                    current_player = player1

                else:
                    current_player = player2

            except Exception as e:
                print("game handler main exception" ,e)      
        self.player1 = None
        self.player2 = None
        self.game_in_progress = False

    def want_to_continue(self,client_detail,win_the_game):
        if not win_the_game:
            #client_detail['client_socket'].send(str(Util.get_info_message(f"\nCongratulations! You sank all ships.")).encode())

            client_detail['client_socket'].send(str(Util.get_info_message(f"\nYou Lost the game.")).encode())
        time.sleep(1)
        while True:
            client_detail["client_socket"].send(str(self.message_util.get_want_to_continue_message()).encode())
            client_message = ast.literal_eval(client_detail["client_socket"].recv(1024).decode())
            data = client_message["data"] #contains ans and session id
            
            if data["answer"] == "y" :
                self.player_registration(client_detail)
            #tp-do else
            break


    def player_rejoin(self, client_detail):
        rejoined = False
        print("rejoin client detail: ", client_detail)
        print("Rejoin player1: ", self.player1)
        print("Rejoin player2: ", self.player2)

        if self.player1 != None and self.player1["client_ID"] == client_detail["client_ID"] and self.player1["session_id"] == client_detail["session_id"]:
            self.player1["client_socket"] = client_detail["client_socket"] 
            self.player1["client_name"] = client_detail["client_name"]
            rejoined = True

        elif self.player2 != None and self.player2["client_ID"] == client_detail["client_ID"] and self.player2["session_id"] == client_detail["session_id"]:
            self.player2["client_socket"] = client_detail["client_socket"] 
            self.player2["client_name"] = client_detail["client_name"]
            rejoined = True

        else:

            for player in self.lobby:
                #to-do: check if earlier socket is active for secuirty
                #to-do: rejoin implementation
                print("rejoin player: ",player)
                if player["client_ID"] == client_detail["client_ID"] and player["session_id"] == client_detail["session_id"]:
                    print("rejoin ; in if ")
                    player["client_socket"] = client_detail["client_socket"] 
                    player["client_name"] = client_detail["client_name"]
                    #to-do : formated message
                    rejoined = True 
                    break

                continue

        if not rejoined:
            #INVALID OR GAME OVER
            rejoin_response= self.message_util.get_rejoin_response(client_detail,"FAIL","ERR001","Invalid session ID/Session timeout.Failed to rejoin")
            client_detail["client_socket"].sendall(str(rejoin_response).encode()) #enter correct session id or leave blank to register again
        
        else: 
            rejoin_response = self.message_util.get_rejoin_response(client_detail,"SUCCESS")
            client_detail["client_socket"].sendall(str(rejoin_response).encode())
        print("rejoin : 1 : " , rejoined)

        return rejoined 


    def player_registration(self, client_detail):
        add_to_lobby = True
        
        for player in self.lobby:
                
            if player["client_ID"] != client_detail["client_ID"]:
                continue

            if player["client_ID"] == client_detail["client_ID"]:
                add_to_lobby = False
                break
          
        if add_to_lobby:
            if client_detail["session_id"] == "" or client_detail["session_id"] == None:
                client_detail["session_id"] = self.generate_sessionID()
                client_detail["timeout_count"] = 0
            self.lobby.append(client_detail)

            #formatted error response
            registration_response = self.message_util.get_registration_response(client_detail,"SUCCESS")
            client_detail["client_socket"].sendall(str(registration_response).encode())
            return True

        else:
            #formatted error response
            registration_response= self.message_util.get_registration_response(client_detail,"FAIL","DUP001","user ID exists")
            client_detail["client_socket"].sendall(str(registration_response).encode())
        return False

               
    def generate_sessionID(self):
        random_num = random.randint(1,1000)
        return str(random_num)

    def manage_lobby(self):
        """
        Manages the lobby and starts a game if at least 2 players are waiting.
        - If a game is already in progress, sleep and retry later.
        - If not, start a new game with the first two players in the lobby.
        - Players remaining in the lobby are notified of their queue position.
        - If fewer than 2 players, notify the player(s) to wait for opponent.
        """
        notify_interval = 0
        failure_count = 0
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
                    self.player1 = player1
                    self.player2 = player2
                    threading.Thread(target=self.game_handler, args=(player1, player2)).start()
                
                if notify_interval == 30:
                    notify_interval = 0 #to-do clean up
                    for i, waiting_player in enumerate(self.lobby): 
                        message = self.message_util.get_queue_wait_message(i, len(self.lobby))
                        
                        try:
                            waiting_player["client_socket"].sendall(str(message).encode())

                            if self.game_in_progress:

                                if self.player1 != None and self.player2 != None:
                                    player1_grid = self.player1["handler"].get_hidden_grid()
                                    player2_grid = self.player2["handler"].get_hidden_grid()

                                    waiting_player["client_socket"].sendall(str(Util.get_grid_message_spectators(f"{self.player1["client_name"]}'s board status", player1_grid , f"{self.player2["client_name"]}'s board status", player2_grid)).encode())

        
                        except Exception as e:
                            print("error in manage lobby ",e)
                            print(f"Failed to notify {waiting_player['client_name']} in lobby.")
                            failure_count += 1

                            if failure_count == 3:                       
                                a = self.lobby.pop(self.lobby.index(waiting_player))
                                print(f"removing {waiting_player["client_name"]} from lobby")
   
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Perform cleanup actions (e.g., closing connections)
            sys.exit(0)

if __name__ == '__main__':
    server = Server('127.0.0.1', 7632)
    server.listen()