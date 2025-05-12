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

class PlayerServerHandler:
    message_util = ServerMessageUtil()

    def __init__(self, client_detail):
        self.client_detail = client_detail
        self.board = Board(client_detail["client_name"])
        self.ships = SHIPS
        self.ship_detail = {}
        self.ship_list = []
        for i in self.ships:
            #print("for i in ships, i : ", i)
            #print("for i in ships, shipname : ", i[0])
            self.ship_detail = {
                "ship_name": i[0],
                "ship_size": i[1],
                "ship_placed": "no",
                "position" : "",
                "direction" : ""
            }
            #print("ship_detail: ", self.ship_detail)
            self.ship_list.append(self.ship_detail)

    def get_client_detail(self):
        return self.client_detail

    def handle(self, message):
        print("player server handler.handle message : ", message)

    def place_ship(self):
        while True:
            current_ship = None

            try:
                for ship_detail in self.ship_list:
                    if ship_detail["ship_placed"] == "no" :
                        current_ship = ship_detail
                        break
                if current_ship == None:
                    self.client_detail["client_socket"].send(str(Util.get_info_message("All ships have been placed. Wait for oponent to place ships")).encode())
                    break
                    
                self.client_detail["client_socket"].send(str(self.message_util.get_place_ship_message(current_ship)).encode())
                client_message = ast.literal_eval(self.client_detail["client_socket"].recv(1024).decode())
                print(client_message)

                try:
                    row, col = parse_coordinate(client_message["data"]["position"])
                    #col = col.upper()
                    if client_message["data"]["direction"] == 'H':
                        orientation = 0

                    elif client_message["data"]["direction"] == 'V':
                        orientation = 1

                    print("orientation = ", orientation)

                    if self.board.can_place_ship(row, col, current_ship["ship_size"], orientation):
                        occupied_positions = self.board.do_place_ship(row, col, current_ship["ship_size"], orientation)
                        self.board.placed_ships.append({
                            'name': client_message["data"]["ship_name"],
                            'positions': occupied_positions
                        })
                        current_ship["ship_placed"] = "yes"
                        
                    
                except (ValueError,IndexError) as e:
                    print(f"  [!] Invalid coordinate: {e}")
                

                if current_ship["ship_placed"] == "no":
                    message = f"  [!] Cannot place {client_message["data"]["ship_name"]} at {client_message["data"]["position"]} (orientation={client_message["data"]["direction"]}). Try again."

                    self.client_detail["client_socket"].send(str(Util.get_info_message(message)).encode())


                

            except Exception as e:
                print("place ship main error",e)

    def fire_at(self, message):
        position = message["data"]["position"]

        if position == None or position == "":
            return None, None , self.board.get_display_grid() , "Timed out or Input not received."
        
        name = self.board.get_player_name()
        print("executing fire command for: ", name)
        sunk_name = None
        try:
            row, col = parse_coordinate(position)
            #col = col.upper()
            result, sunk_name = self.board.fire_at(row, col)

            if result == 'hit':
                if sunk_name:
                    return_message = f"  >> HIT! You sank the {sunk_name}! \n Opponent board status: "
                else:
                    return_message = "  >> HIT! \n Opponent board status: "
                if self.board.all_ships_sunk():
                    self.board.print_display_grid()
                    return_message = "\nCongratulations! You sank all ships. \n Opponent board status: "

            elif result == 'miss':
                return_message = "  >> MISS! \n Opponent board status: "

            elif result == 'already_shot':
                return_message =  "  >> You've already fired at that location. Try again. \n Opponent board status: "
            
        except ValueError as e:
            print("  >> Invalid input:", e)
            return_message = "Invalid coordinates. Try again. \n Opponent board status: "
            result = 'miss'

        except Exception as e:
            print("error fire at: ", e)
            return_message = f" Unexpected Error occured - {e}. Try again. \n Opponent board status: "
            result = 'miss'

        display_grid = self.board.get_display_grid()
        return result, sunk_name, display_grid, return_message

    def is_game_over(self):
        return self.board.all_ships_sunk()

    def get_hidden_grid(self):
        return self.board.get_hidden_grid()

 
                
            
            

        
