

class ServerMessageUtil:

    def __init__(self):
        print(1)
    
    def get_registration_response(self, client_detail,status,error_code = "",error_message = ""):

        if status == "SUCCESS":

            message = {"message_type": "RESPONSE", "response_status": status ,"command": "REGISTER" , "response_message" : f"Successfully registered with session ID {client_detail["session_id"]}","data":{ "session_id" : client_detail["session_id"]}}

            return message

        elif status == "FAIL":
            message = {"message_type": "RESPONSE", "response_status": status ,"command": "REGISTER" , "response_message" : f"Failed registeration with error code: {error_code},{error_message}", "error_code": error_code}

            return message
    
    def get_rejoin_response(self, client_detail,status,error_code = "",error_message = ""):

        if status == "SUCCESS":

            message = {"message_type": "RESPONSE", "response_status": status ,"command": "REGISTER" , "response_message" : f"Successfully rejoined with session ID {client_detail["session_id"]}","data":{ "session_id" : client_detail["session_id"]}}

            return message

        elif status == "FAIL":
            message = {"message_type": "RESPONSE", "response_status": status ,"command": "REGISTER" , "response_message" : f"Failed rejoin with error code: {error_code},{error_message}", "error_code": error_code}

            return message


    def get_queue_wait_message(self, position, queue_length):

        if queue_length < 2 :
            message = {"message_type": "INFO", "message" : "Waiting for opponent to join."}
            return message

        else:
            message = {"message_type": "INFO", "message" : f"You are at {position}. Please wait your turn"}
            return message

    def get_place_ship_message(self, ship_detail):

        message = {"message_type" : "ACTION", "message":"Game started. Your turn to place the ship", "command" : "PLACE_SHIP", "data":ship_detail }
        #print(message)
        return message

    def get_fire_request(self):
       message = {"message_type" : "ACTION", "message":"\nEnter coordinate to fire at (or 'quit'): ", "command" : "FIRE"}
       return message

    def get_want_to_continue_message(self):

        message = {"message_type" : "ACTION", "message": "\nDo you want to continue playing?(y/n): ", "command" : "CONTINUE"}
        return message

    def send_chat_message(self, message):
        message = {"message_type" : "CHAT", "message": message, "command" : ""}
        return message

    

