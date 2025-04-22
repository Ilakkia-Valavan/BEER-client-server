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

        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        self.players = []    # Max 2
        self.lobby = []      # Waiting players
        self.spectators = [] # Spectators

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



    def handle_lobby(self, player):
        print(f"{player['client_name']} entered the lobby.")
        self.manage_game()  # This checks the lobby for game readiness


    def manage_game(self):
    """
    Manages the lobby and starts a game if at least 2 players are waiting.
    """

        while True:
            with self.lobby_lock:
                if len(self.lobby) < 2:
                    break  

                
                player1 = self.lobby.pop(0)
                player2 = self.lobby.pop(0)

            try:
                player1['client_socket'].send("You are matched with an opponent. Game starting...\n".encode())
                player2['client_socket'].send("You are matched with an opponent. Game starting...\n".encode())
            except:
                print("Failed to notify one or both players. Skipping match.")
                continue

            time.sleep(1)  

            # Start game
            threading.Thread(target=self.handle_player, args=(player1, player2)).start()

    def handle_player(self, player1, player2):

        print(f"Match started between {player1['client_name']} and {player2['client_name']}")
        
        #replace this with game

        try:
            player1['client_socket'].send("Match in progress... \n".encode())
            player2['client_socket'].send("Match in progress... \n".encode())
            time.sleep(10)  # Simulate match time
        except:
            print("Error during match.")

        finally:
            # After match ends decide what to do
            try:
                player1['client_socket'].send("Game over. Going back to lobby...\n".encode())
                player2['client_socket'].send("Game over. Going back to lobby...\n".encode())
            except:
                print("One of the players disconnected after the match.")
            
            self.handle_lobby(player1)
            self.handle_lobby(player2) #dshld i send as thread?


    def player_registration(self, client_detail):
        print("player_registration:1")
        add_to_lobby = True
        for player in self.lobby:
            if player["client_ID"] != client_detail["client_ID"]:
                continue
            if player["client_ID"] == client_detail["client_ID"] and player["client_name"] != client_detail["client_name"]:
                client_detail["client_socket"].send("Client ID exists. Please connect with different client ID".encode())
                add_to_lobby = False
                break

            elif player["client_ID"] == client_detail["client_ID"] and player["client_name"] == client_detail["client_name"]:
                client_detail["client_socket"].send("re-joined in waiting lobby".encode())
                #to-do: check if earlier socket is active for secuirty
                player["client_socket"] = client_detail["client_socket"] 
                add_to_lobby = False
                break
            
            if add_to_lobby:
                self.lobby.append(client_detail)
                threading.Thread(target=self.handle_lobby, args=(client_detail,)).start()
                    

if __name__ == '__main__':
    server = Server('127.0.0.1', 7632)
    server.listen()




 