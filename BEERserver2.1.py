import ast
import socket
import threading

class Server:
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen()
        self.lobby_lock = threading.Lock()
        self.game_in_progress = False 

        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        self.players = []    # Max 2
        self.lobby = []      # Waiting players
        self.spectators = [] # Spectators
        threading.Thread(target=self.manage_game).start() #will run in background

    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from: " + str(address))

            try:
                client_detail = ast.literal_eval(client_socket.recv(1024).decode())
                client_detail["client_socket"]=client_socket


                role = client_detail["client_role"].upper() 

                if role == 'P':
                    print(4)
                    self.player_registration(client_detail) 
                    
                    
                elif role == 's':  
                    # Spectator
                    self.spectators.append(client_detail)
                    client_socket.send("You have choses spectator.\n".encode())
                    threading.Thread(target=self.handle_new_spectator, args=(client_detail,)).start()

            except Exception as error:
                print("An error occurred:", error) # An error occurred: name 'x' is not defined
                continue




    def handle_new_spectator(self, spectator):
        client_name = spectator['client_name']
        client_socket = spectator['client_socket']

        while True:
            try:
                client_message = client_socket.recv(1024).decode()
                #handles peple who are not players and not in waiting list but only wish to spectate
                
            except:
                break


    #no need handle_lobby()
    def handle_lobby(self, player):
        print(f"{player['client_name']} entered the lobby.")
        self.manage_game() #call as thread 


    def manage_game(self):
        """
        Manages the lobby and starts a game if at least 2 players are waiting.
        - If a game is already in progress, sleep and retry later.
        - If not, start a new game with the first two players in the lobby.
        - Players remaining in the lobby are notified of their queue position.
        - If fewer than 2 players, notify the player(s) to wait for opponent.
        """
        while True:
            with self.lobby_lock:
                if self.game_in_progress:
                    time.sleep(1)
                    continue

                if len(self.lobby) < 2:
                    for i, waiting_player in enumerate(self.lobby):
                        message = f"Waiting for opponent... You are position #{i+1} in queue."
                        try:
                            waiting_player["client_socket"].send(message.encode())
                        except:
                            print(f"Failed to notify {waiting_player['client_name']} in lobby.")
                    time.sleep(1)
                    continue

                # Start new game
                self.game_in_progress = True
                player1 = self.lobby.pop(0)
                player2 = self.lobby.pop(0)

                print(f"Starting game between {player1['client_name']} and {player2['client_name']}.")
                threading.Thread(target=self.handle_game, args=(player1, player2)).start()

            time.sleep(1)  

            

    def handle_game(self, player1, player2):
        print(f"Match started between {player1['client_name']} and {player2['client_name']}")

        try:
            # Initial match intro
            player1['client_socket'].send("Match started! You are Player 1.\n".encode())
            player2['client_socket'].send("Match started! You are Player 2.\n".encode())

            for player in [player1, player2]:
                player['client_socket'].send("Phase 1: Place your ships. Use format: PLACE <ShipName> <Coord> <H/V>\n".encode())

            # Simulate ship placement input
            for player in [player1, player2]:
                ship_count = 0
                while ship_count < len(SHIPS):
                    try:
                        msg = player['client_socket'].recv(1024).decode().strip()
                        player['client_socket'].send(f"placed: {msg}\n".encode())
                        ship_count += 1
                    except:
                        player['client_socket'].send("Invalid input or connection issue.\n".encode())
                        break

            # Game logic loop
            player1['client_socket'].send("Game starting. Your turn. FIRE <Coord>\n".encode())
            player2['client_socket'].send("Wait for your turn...\n".encode())

            game_over = False
            current_turn = 0
            players = [player1, player2]

            while not game_over:
                attacker = players[current_turn]
                defender = players[1 - current_turn]

                attacker['client_socket'].send("Your turn: FIRE <Coord>\n".encode())
                coord = attacker['client_socket'].recv(1024).decode().strip()

                result_msg = f"{attacker['client_name']} fired at {coord}\n"
                attacker['client_socket'].send(f"Result: {result_msg}".encode())
                defender['client_socket'].send(f"{attacker['client_name']} fired at {coord}\n".encode())

                if coord.lower() == 'z10':  # dummy end condition
                    game_over = True
                    break

                current_turn = 1 - current_turn

            # Ask if they want to play again
            responses = {}
            for player in [player1, player2]:
                try:
                    player['client_socket'].send("Game over! Do you want to play another match? (yes/no)\n".encode())
                    reply = player['client_socket'].recv(1024).decode().strip().lower()
                    responses[player['client_name']] = reply
                except:
                    responses[player['client_name']] = 'no'

            # Re-add to lobby based on responses
            if responses.get(player1['client_name'], 'no') == 'yes':
                self.lobby.append(player1)
                player1['client_socket'].send("You've been re-added to the lobby.\n".encode())
            else:
                player1['client_socket'].send("Thanks for playing! Disconnecting...\n".encode())
                player1['client_socket'].close()

            if responses.get(player2['client_name'], 'no') == 'yes':
                self.lobby.append(player2)
                player2['client_socket'].send("You've been re-added to the lobby.\n".encode())
            else:
                player2['client_socket'].send("Thanks for playing! Disconnecting...\n".encode())
                player2['client_socket'].close()

        except Exception as e:
            print("Error during match:", str(e))

        finally:
            self.game_in_progress = False



    def player_registration(self, client_detail):
        print("player_registration:1")
        add_to_lobby = True
        for player in self.lobby:
            if player["client_ID"] != client_detail["client_ID"]:
                continue
            if player["client_ID"] == client_detail["client_ID"] and player["client_name"] != client_detail["client_name"]:
                add_to_lobby = False
                break

            elif player["client_ID"] == client_detail["client_ID"] and player["client_name"] == client_detail["client_name"] and client_detail["session_id"]= not null and player["session_id"] == client_detail["session_id"]:
                client_detail["client_socket"].send("re-joined in waiting lobby".encode())
                #to-do: check if earlier socket is active for secuirty
                player["client_socket"] = client_detail["client_socket"] 
                add_to_lobby = False
                break
          
        if add_to_lobby:
                #to-do add session id to client_detail
                client_detail["session_id"] = generate_unique_sessionID()
                self.lobby.append(client_detail)

                registration_response=
                {{header: response_status: "sucess", session_id= client_detail["session_id"]},{error: error_code:"",error_message:""}}
                #send message to client "sucessfully registered! with {session_id}. please use thi id to rejoin of dropped" info message
                client_detail["client_socket"].send(registration_response.encode())

                threading.Thread(target=self.handle_lobby, args=(client_detail,)).start() #no need tp start thread

        else:
            #formatted error response here
                registration_response ={header:{​response_status: “fail”​,session_id:” ”​}​,error:{​error_code:”DUP0908”,​error_message: “user ID exists…”​}}
                    

if __name__ == '__main__':
    server = Server('127.0.0.1', 7632)
    server.listen()




 