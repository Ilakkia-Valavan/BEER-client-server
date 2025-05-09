class ClientMessageUtil:

    def __init__(self):
        print(1)
    
    def get_registration_message(self, client_detail):

        message = {"message_type": "ACTION", "command": "REGISTER" , "data":{"client_name": client_detail["client_name"], "client_ID" : client_detail["client_ID"], "client_role": client_detail["client_role"], "session_id" : client_detail["session_id"]}}

        return message

    def get_ship_placement_message(self, ship_detail, position, direction, client_detail):

        message = {"message_type": "ACTION", "command": "PLACE_SHIP" , "data":{"ship_name": ship_detail["ship_name"], "position" : position, "direction": direction, "session_id" : client_detail["session_id"]}}

        return message

    def get_fire_command(self,client_detail, position):
        message = {"message_type": "ACTION", "command": "FIRE" , "data":{ "position" : position, "session_id" : client_detail["session_id"]}}

        return message

    def get_continue_message(self,client_detail, answer):
        message = {"message_type": "ACTION", "command": "CONTINUE" , "data":{ "answer" : answer, "session_id" : client_detail["session_id"]}}

        return message