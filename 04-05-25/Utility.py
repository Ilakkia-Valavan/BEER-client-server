class Util:

    def __init__(self):
        print("")

    @staticmethod
    def print_info(message):
        print("\033[0;34m INFO: " + message + "\033[0m")
    
    @staticmethod
    def print_error(message):
        print("\033[1;31;40m ERROR: " + message + "\033[0m")

    @staticmethod
    def get_info_message(message):
        message = {"message_type": "INFO", "message" : message}
        return message

    @staticmethod
    def get_prompt_message(message):
        return "\033[0;32m INPUT: " + message + "\033[0m :   "

    @staticmethod
    def get_info_message_grid(message, display_grid):
        message = {"message_type": "INFO", "message" : message, "display_grid" : display_grid}
        return message

    @staticmethod
    def get_grid_message_spectators(player1_message , player1_grid, player2_message , player2_grid):
        message = {"message_type": "INFO","message" : "" ,"player1_message" : player1_message, "player2_message" : player2_message,"player1_grid" : player1_grid, "player2_grid" : player2_grid}
        return message

    @staticmethod
    def print_chat_message(message,sender):
        print(f"\033[0;34m [CHAT] {sender}: " + message + "\033[0m")



