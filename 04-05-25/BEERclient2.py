#client program for beer server 3
import sys
import socket
import threading
import ast
from ClientMessageUtil import ClientMessageUtil 
from Utility import Util 
import logging
import time
import msvcrt
import logging
import curses



class Client:
    #logging.basicConfig(level=logging.DEBUG)
    #logger = logging.getLogger('beer')
    

    def __init__(self, HOST, PORT):
        self.logger = logging.getLogger()

        self.logger.setLevel(logging.DEBUG)
        self.logger.info("hello")

        self.chat_messages = []


        self.receive = True
        self.ship_detail={}
        self.ship_list=[]
        self.size = 10
        """
        self.name = input("Enter your name: ")
        self.ID = input("Enter your ID: ")
        self.session_id = input("Enter session ID if rejoining (or leave blank): ").strip()
        self.role = input("Enter your role (p = Player, s = Spectator): ").lower().strip()
        self.message_util = ClientMessageUtil()

        self.client = {
            'client_name': self.name,
            'client_ID': self.ID,
            'client_role': self.role,
            'session_id': self.session_id
        }
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        #print(f"[CONNECTED] Connected to server at {HOST}:{PORT}")
        self.logger.debug(f"[CONNECTED] Connected to server at {HOST}:{PORT}")

        self.name = input("Enter your name: ")
        if self.name == "":
            self.name = input("Please enter valid  name: ")

        self.ID = input("Enter your ID: ")
        if self.ID == "":
            self.ID = input("Please enter ID : ")

        self.role = input("Enter your role (p = Player, s = Spectator): ").lower().strip()

        if self.role.lower() != "p" and self.role.lower() != "s":
            self.role = input("Enter valid role (p = Player, s = Spectator): ").lower().strip()

        if self.role.lower() == 'p' :
            self.player_registration()
        
        elif self.role.lower() == "s":
            self.spectator_register()

    def get_user_input(self, prompt_message):
        timeout = 30  # seconds
        print(prompt_message)
        start_time = time.time()
        char = None
        while True:
            if msvcrt.kbhit():
                char = sys.stdin.readline()
                print("You entered:", char.strip())
                break
            if time.time() - start_time > timeout:
                print("Timeout: no input received.")
                break
            time.sleep(0.1)

        return char

    def spectator_register(self, response_message = None):
        self.client = {
                'client_name': self.name,
                'client_ID': self.ID,
                'client_role': self.role,
            }
        self.message_util = ClientMessageUtil()
        message = self.message_util.get_spectator_registration_message(self.client)
        self.socket.sendall(str(message).encode())
        threading.Thread(target=self.receive_and_interact_with_server_spectator).start()
        self.start_chat_loop(stdscr)

    def receive_and_interact_with_server_spectator(self):
        while True:
            print("in while loop")
            try:           
                message = self.socket.recv(4096).decode()
                #print("receive_and_interact_with_server-> " ,message)

                # Try to parse as dict (structured message)
                try:
                    
                    server_message = ast.literal_eval(message)
                    if server_message["message_type"] == "CHAT":
                        print("chat list client side :" ,server_message)
                        chat_list = server_message["chat_list"]
                        for i in chat_list:                           
                            chat_entry = ast.literal_eval(i)
                            self.chat_messages.append(f"{chat_entry['sender']}: {chat_entry['message']}")
                            #Util.print_chat_message(chat_entry["message"], chat_entry["sender"])

                    
                            
                    if server_message["message_type"] == "GAME_LOG":
                        print("game log list client side :" ,server_message)
                        game_log_list = server_message["game_log_list"]
                        for i in game_log_list:
                            game_log = ast.literal_eval(i)
                            Util.print_game_log_message(game_log["current_player"], game_log["result"], game_log["return_message"])
                    


                    elif server_message["message_type"] == "INFO":
                        Util.print_info(server_message["message"])
                        if "display_grid" in server_message and server_message["display_grid"] != None:
                            #print("grid part : ",server_message)
                            #self.print_display_grid(server_message["display_grid"])
                            self.print_display_grid_spectator(server_message["display_grid"],stdscr)
                            
                            


                        if "player1_grid" in server_message:
                            #Util.print_info(server_message["player1_message"])
                            #self.print_display_grid(server_message["player1_grid"])
                            self.print_display_grid_spectator(server_message["player1_grid"],stdscr)
                            
                            #Util.print_info(server_message["player2_message"])
                            #self.print_display_grid(server_message["player2_grid"])
                            self.print_display_grid_spectator(server_message["player2_grid"],stdscr)
                        
                except Exception as e:
                    print(f"[CHAT ERROR] {e}")

            except Exception as e:
                    print(f"[CHAT ERROR] {e}")
                    break
    """
    def start_chat_loop(self):
        def chat_loop():
            while True:
                try:
                    prompt_message = Util.get_prompt_message("Enter CHAT message: ")
                    msg = input()  # Accept chat message
                    if msg.strip():
                        self.socket.sendall(str(self.message_util.get_chat_messages(msg,self.client)).encode())
                except:
                    break
        threading.Thread(target=chat_loop).start()
    """

    def print_display_grid_spectator(self, grid_to_print, stdscr):
        # Clear previous content in the window
        stdscr.clear()

        # Get the terminal height and width to ensure content fits
        height, width = stdscr.getmaxyx()

        # Calculate the board's width and set up the starting column for the board
        board_width = width // 2  # Left half for the board
        start_col = 0  # Start printing the board from column 0
        start_row = 0  # Start printing from row 0

        # Column headers (1 .. N)
        column_headers = "  " + "".join(str(i + 1).rjust(2) for i in range(self.size))
        stdscr.addstr(start_row, start_col, column_headers)  # Print column headers

        # Print each row, labeled with A, B, C, ...
        for r in range(self.size):
            row_label = chr(ord('A') + r)  # Row labels A, B, C, ...
            row_str = " ".join(grid_to_print[r][c] for c in range(self.size))
            row_output = f"{row_label:2} {row_str}"
            stdscr.addstr(start_row + r + 1, start_col, row_output)  # Print each row below the headers

        # Refresh the screen to update the window
        stdscr.refresh()

    def start_chat_loop(self, stdscr):
        def chat_loop():
            while True:
                try:
                    prompt_message = Util.get_prompt_message("Enter CHAT message: ")
                    stdscr.addstr(0, 0, prompt_message)  # Print prompt message in the terminal
                    stdscr.refresh()

                    msg = input()  # Accept chat message
                    if msg.strip():
                        self.socket.sendall(str(self.message_util.get_chat_messages(msg,self.client)).encode())
                except:
                    break
        threading.Thread(target=chat_loop).start()



        


    def player_registration(self, response_message = None):
        print("in player_registration 1")
        if response_message == None : 
               
            if self.role.lower() == "p":
                self.session_id = input("Enter session ID if rejoining (or leave blank): ").strip()

            self.message_util = ClientMessageUtil()

            self.client = {
                'client_name': self.name,
                'client_ID': self.ID,
                'client_role': self.role,
                'session_id': self.session_id
            }
            message = self.message_util.get_registration_message(self.client)
            self.socket.sendall(str(message).encode())
            threading.Thread(target=self.receive_and_interact_with_server).start()
        
        else:
            print(response_message["response_message"])
            if response_message["response_status"] == "FAIL" and response_message["error_code"] == "DUP001":
                self.ID = input(f"Enter a different ID(Not same as {self.client["client_ID"]}): ")
                self.client["client_ID"] = self.ID
                message = self.message_util.get_registration_message(self.client)
                print("in player_registration 2")
                print(message)
                self.socket.sendall(str(message).encode()) 
                self.receive = True
            
            elif response_message["response_status"] == "FAIL" and response_message["error_code"] == "ERR001":
                self.session_id = input(f"Enter correct session ID (or leave blank to register anew): ")
                self.client["session_id"] = self.session_id
                message = self.message_util.get_registration_message(self.client)
                print("in player_registration 2")
                print(message)
                self.socket.sendall(str(message).encode()) 
                self.receive = True
            
            else:
                self.client["session_id"] = response_message["data"]["session_id"]
                Util.print_info(response_message["response_message"])


    def action_handler(self, server_message):
        if server_message["command"] == "PLACE_SHIP":
            ship_detail = server_message["data"]

            message = Util.get_prompt_message(f"Input position to place the ship {ship_detail["ship_name"]} - {ship_detail["ship_size"]}")
            position = input(message)

            message = Util.get_prompt_message(f"Input direction(Horizontal/Vertical) to place the ship <H/V> ")
            direction = input(message)

            message = self.message_util.get_ship_placement_message(ship_detail, position, direction.upper(), self.client)

            print("place ship: ", message)
            self.socket.sendall(str(message).encode())

        elif server_message["command"] == "FIRE":
            message = Util.get_prompt_message(server_message["message"] + " (within 30 seconds.)")
            #inputs, outputs, errors = select.select([sys.stdin], [], [], 20)
            #print("action handler input timeout 1: inputs: ", inputs,"outputs: " , outputs,"errors: ",errors)
            #position = input(message)
            position = self.get_user_input(message)
            message = self.message_util.get_fire_command(self.client, position)
            self.socket.sendall(str(message).encode())

        elif server_message["command"] == "CONTINUE":
            message = Util.get_prompt_message(server_message["message"])
            answer = input(message)
            message = self.message_util.get_continue_message(self.client,answer)
            self.socket.sendall(str(message).encode())

    def print_display_grid(self, grid_to_print):
        """
        Print the board as a 2D grid.
        
        If show_hidden_board is False (default), it prints the 'attacker' or 'observer' view:
        - '.' for unknown cells,
        - 'X' for known hits,
        - 'o' for known misses.
        
        If show_hidden_board is True, it prints the entire hidden grid:
        - 'S' for ships,
        - 'X' for hits,
        - 'o' for misses,
        - '.' for empty water.
        """
        # Decide which grid to print
        #grid_to_print = self.hidden_grid if show_hidden_board else self.display_grid

        # Column headers (1 .. N)
        print("  " + "".join(str(i + 1).rjust(2) for i in range(self.size)))
        # Each row labeled with A, B, C, ...
        for r in range(self.size):
            row_label = chr(ord('A') + r)
            row_str = " ".join(grid_to_print[r][c] for c in range(self.size))
            print(f"{row_label:2} {row_str}")

    def receive_and_interact_with_server(self):
        print("in thread func")
        while True:
            print("in while loop")
            try:           
                message = self.socket.recv(4096).decode()
                print("receive_and_interact_with_server-> " ,message)

                # Try to parse as dict (structured message)
                try:
                    #change
                    server_message = ast.literal_eval(message)

                    if server_message["message_type"] == "RESPONSE" and server_message["command"] == "REGISTER":
                        #self.player_registration(server_message)
                        threading.Thread(target=self.player_registration, args=(server_message,)).start()

                    elif server_message["message_type"] == "INFO":
                        Util.print_info(server_message["message"])
                        if "display_grid" in server_message and server_message["display_grid"] != None:
                            #print("grid part : ",server_message)
                            self.print_display_grid(server_message["display_grid"])

                        if "player1_grid" in server_message:
                            Util.print_info(server_message["player1_message"])
                            self.print_display_grid(server_message["player1_grid"])

                            Util.print_info(server_message["player2_message"])
                            self.print_display_grid(server_message["player2_grid"])

                    elif server_message["message_type"] == "ACTION":
                        self.action_handler(server_message)

                    print("in thread func 2")

                except Exception as e:
                    print(f"[ERROR receive_and_interact_with_server] {e}")

                # Print regular server messages in red
                #print("\033[1;31;40m" + message.strip() + "\033[0m")



            except Exception as e:
                print(f"[ERROR] {e}")
                break
        print("out while loop")

        self.socket.close()
        print("[CLOSED] Connection closed.")


"""
if __name__ == '__main__':
    Client('127.0.0.1', 7632)
"""

import curses

def main(stdscr):
    # Initialize the Client with stdscr
    client = Client('127.0.0.1', 7632)  # Pass the host and port to the Client

# Run the curses application
if __name__ == '__main__':
    curses.wrapper(main)

